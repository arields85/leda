# ADR 0019: La evidencia de la entrega y la página de la tarea

- **Estado:** aceptado por el usuario el 2026-10-07, con sus cinco respuestas a las preguntas del
  borrador. La decisión de origen es del usuario; el resto fue la propuesta del agente.
- **Fecha:** abierta el 2026-10-07.
- **Alcance:** cómo recibe y guarda Leda la evidencia de una entrega (texto, fotos y archivos por
  Telegram), cómo la lleva a quien aprueba y la página de sólo lectura de una tarea, que es el primer
  pedazo de la plataforma web (ADR 0017, decisión 5).
- **Evidencia:** `odd/tasks/fase-c.md`, preguntas 1 a 3; relevamiento del 2026-10-07 de
  `db/esquema.sql` (`evidence`, `task_evidence_policy`, `evidencia_pendiente`, `message_outbox`,
  `acceso_tablero`, las políticas de aislamiento y los dueños de las funciones), `src/leda/tablero.py`,
  `src/leda/entrada.py`, `src/leda/herramientas.py` (`actualizar_estado`, `adjuntar_evidencia`,
  `_notificar_entrega_al_aprobador`, `_enlace_portal_tarea`), `src/leda/motor/recibir.py`,
  `src/leda/despachador.py` y `espacios/corework.yaml` (`evidencia.por_area`); ADR 0004, 0009, 0017
  y 0018; `docs/architecture/frontera.md`.

## Contexto

La Fase C empieza por la entrega y la aprobación (circuitos 7 y 8). Hoy:

- **Una foto sin texto se ignora** y un archivo también: `recibir.py` sólo atiende `text`.
- **La evidencia es sólo texto.** `evidence` tiene `uri`, `drive_file_id` y `sha256`, pero sólo se
  escribe texto en `uri`. `leda_app` puede modificar y borrar sus filas.
- **La política se cumple con una fila cualquiera.** `evidencia_pendiente` mira si existe alguna
  evidencia del ciclo vigente, sin comparar con los tipos que pide la política del área. En CoreWork,
  electricidad pide `[explicacion, foto]`: hoy una frase sola la cumple, contra la mecánica §6.
- **El aviso a quien aprueba es texto fijo**, armado fuera del motor, y la salida sólo manda texto.
- **No hay página de una tarea.** Existe el tablero de sólo lectura por espacio (`/tablero/{token}`)
  y un punto de enganche que hoy no devuelve nada (`_enlace_portal_tarea`).

## Decisiones

### 1. Lo que decidió el usuario (usuario, 2026-10-07)

Leda acepta como evidencia de una entrega texto, fotos y archivos mandados por Telegram. Se guardan
en la base, con su huella y atados a su espacio; después se puede mover el almacenamiento sin
cambiar lo demás. El aviso a quien aprueba lleva las fotos adjuntas y un enlace a una página de la
tarea, de sólo lectura, con su evidencia y su historia. La página es como el tablero de hoy: enlace
personal y sólo lo que esa persona puede ver. Es el primer pedazo de la plataforma, y por eso este
ADR va antes del código.

**Vencimiento del enlace: ofrecido y no elegido** (usuario, 2026-10-07). El enlace de la página no
vence, a diferencia del tablero (30 minutos por defecto). La decisión 6 dice qué lo acota.

### 2. Los archivos van en una tabla propia, como `bytea`

Una tabla nueva, `archivo`, guarda el contenido de cada archivo recibido, separado de la evidencia:

- **Columnas:** `workspace_id`, el contenido (`bytea`), su `sha256`, el tamaño, el tipo detectado,
  el nombre original, quién lo mandó y cuándo. Ningún identificador de Telegram (frontera, regla 2).
- **La huella la garantiza la base:** un `check` exige que `sha256` sea el de su contenido. Un mismo
  archivo mandado dos veces en un espacio se guarda una vez (único por espacio y huella); nunca se
  comparte entre espacios.
- **Aislamiento:** `row level security` forzado con la política de siempre, y entra en la lista de
  tablas que recorre la prueba de aislamiento. Toda función `security definer` que la toque tiene
  dueño explícito, `leda_owner`.
- **La evidencia apunta al archivo**, con clave foránea compuesta por espacio y id (el patrón de la
  migración `0030`). Mover el almacenamiento después es cambiar dónde vive el contenido de `archivo`,
  con la huella para verificar la copia; `evidence` no cambia.
- **Aparte de `evidence`** para que ninguna lectura de la evidencia, del tablero o de los avisos
  arrastre el contenido.

**Límites:**

- **Tamaño:** 60 MB por archivo (usuario, 2026-10-07). Es un límite del producto, que un espacio
  puede bajar con `workspace_setting`. El canal tiene el suyo: la API de bots de Telegram deja
  descargar hasta 20 MB (core.telegram.org/bots/api, objeto `File`), y sin límite con un servidor
  propio de la API de bots. Mientras no esté ese servidor rige el del canal, 20 MB; se instala cuando
  Leda vaya a un equipo real, con el resto de la operación. Que Telegram no deje bajar más es un
  límite del adaptador, no la regla de negocio (frontera, regla 3).
- **Tipo:** lista permitida del producto, igual para todos los clientes, juzgada por el contenido y
  no por la extensión ni por el tipo que declara quien manda: imágenes (JPEG, PNG, WebP, HEIC), PDF,
  documentos de oficina, texto plano, CSV y videos (usuario, 2026-10-07). También comprimidos y archivos
  de proyecto, como el programa exportado de un PLC (usuario, 2026-10-07): Leda nunca los abre ni los
  ejecuta, y la página los ofrece sólo para descargar. Quedan afuera los ejecutables sueltos, los
  scripts, el HTML y el SVG (que pueden ejecutar código en el navegador de quien los abre).
- **Fuera de límite:** Leda lo dice en palabras de todos los días y propone qué hacer (mandarlo
  como foto, uno más corto o un enlace). Nunca lo descarta en silencio. Un enlace (por ejemplo, a un
  video en Drive) es evidencia de la clase enlace (decisión 5).

**Alternativas descartadas:**

- **Objetos grandes de PostgreSQL** (`lo_*`): `pg_largeobject` no tiene `row level security`, sólo
  permisos por objeto, y deja huérfanos que hay que limpiar aparte. Rompe la invariante número uno.
- **El sistema de archivos o un almacenamiento de objetos:** queda fuera de la transacción (la fila y
  el archivo pueden quedar desparejos), fuera de la política de aislamiento y fuera del respaldo de
  la base. Es el destino natural si el volumen crece, y la tabla `archivo` está pensada para mudarse
  ahí sin tocar la evidencia.
- **Google Drive**, que el pack de CoreWork declara (`almacenamiento: google_drive`) y el ADR 0010
  proponía: este ADR lo reemplaza para la evidencia, por decisión del usuario (la base).

### 3. Una evidencia no se edita ni se borra

- **`leda_app` sólo agrega:** se le quitan `update` y `delete` sobre `evidence` y `archivo`, y un
  disparador rechaza cualquier modificación, como en los eventos de estado.
- **Un archivo equivocado se retira, no se borra.** "No, esa foto no era" agrega un hecho de retiro
  (tabla `evidencia_retirada`: qué evidencia, quién, por qué, cuándo; sólo se agrega). Es la
  situación general de la corrección (ADR 0018, decisión 4, y 9f: se agrega, no se borra). Puede
  retirarla quien la entregó mientras la tarea no esté aprobada. La evidencia retirada no cuenta para
  la política, no va en el aviso y en la página figura como retirada.
- **Retiro de contenido por la administración:** si una foto muestra algo que no debía quedar
  guardado (por ejemplo, una contraseña escrita en un papel), sólo el administrador de plataforma,
  por su canal, puede borrar el contenido de `archivo`. La fila de evidencia y su huella quedan; el
  acto queda en `audit_log` con quién, cuándo y por qué, y la página dice "retirado por la
  administración".
- **Conservación:** como las conversaciones (ADR 0002 y ADR 0018, decisión 3): sin vencimiento hasta
  que un administrador autorizado lo borre, con el borrado registrado. Un archivo recibido que nunca
  pasó a ser evidencia es parte de la conversación y se conserva igual.

### 4. Cómo llega un archivo por Telegram

- **El adaptador lo baja antes del turno.** `recibir.py` atiende también foto (la de mayor
  resolución) y documento, con o sin texto. Comprueba tamaño y tipo, guarda el contenido en `archivo`
  y lo ata al mensaje entrante en una tabla del lado del transporte (`archivo_de_mensaje`, con el
  identificador de Telegram del archivo, como `inbound_message` guarda el `chat_id`). Si la descarga
  falla, se reintenta como cualquier update y, al agotarse, incidente y texto fijo a la persona
  (ADR 0018, decisión 8): nunca en silencio.
- **Un álbum es un solo mensaje.** Telegram manda cada foto de un álbum como un update aparte, con el
  mismo grupo. El adaptador las junta en un solo turno, con una espera corta: una respuesta por
  mensaje (ADR 0013). El valor de la espera se fija en el plan.
- **La IA sabe que llegó un archivo, no lo mira.** Recibe como hecho "una foto", "un archivo
  `informe.pdf`" y el texto que vino con ellos. No juzga el contenido: eso es de quien aprueba
  (constitución §3 y §11). Elige la jugada como con cualquier mensaje (ADR 0018, decisión 1).
- **Con una entrega abierta,** el archivo se suma a esa entrega: el estado de la conversación dice que
  Leda la estaba esperando (ADR 0018, decisión 3, el ejemplo de la foto del tablero).
- **Sin una entrega abierta,** Leda pregunta para qué es, como ante cualquier duda (situación general
  5). El archivo queda guardado como parte de la conversación y no cuenta como evidencia hasta que
  una entrega lo tome. **Lo mandado antes cuenta si se incluye al confirmar** (usuario, 2026-10-07):
  la vista previa de la entrega muestra también lo que llegó durante la tarea ("la foto del martes y
  la de hoy") y la persona confirma o saca alguna. Nada entra sin que la persona lo vea.

### 5. La entrega junta la evidencia y la política se cumple por tipo

- **La vista previa de la entrega muestra cada pieza** ("una foto, un PDF y lo que escribiste") y su
  huella incluye la de cada archivo. Se confirma con el botón o por escrito, con la guarda de la
  decisión 2 del ADR 0018: si llegó o se retiró una pieza después de mostrarla, la confirmación
  escrita no vale y Leda muestra lo nuevo. Al confirmar, las filas de evidencia y el paso a revisión
  se escriben en el mismo acto (patrón del ADR 0009).
- **Cada evidencia guarda su clase:** texto, imagen, archivo o enlace. La clase la fija el código por
  el contenido, nunca la IA.
- **Cada tipo de la política acepta ciertas clases**, y eso es dato del pack, versionado con la
  política (frontera, regla 5), no código. Propuesta para CoreWork: `explicacion` ← texto; `foto` y
  `captura` ← imagen; `archivo` ← archivo, imagen o enlace; `resultado_de_prueba` ← texto, archivo,
  imagen o enlace (usuario, 2026-10-07: un resultado de prueba se puede contar por escrito).
- **`evidencia_pendiente` cambia:** la política se cumple cuando cada tipo pedido tiene una pieza
  propia del ciclo vigente, no retirada, de una clase que ese tipo acepta. Un mismo texto puede cubrir
  varios tipos ("terminé, lo probé 20 ciclos sin falla" es explicación y resultado de la prueba): la
  vista previa de la entrega dice qué cubre cada pieza y la persona lo confirma o lo corrige (usuario,
  2026-10-07). Con eso, en electricidad una frase sola ya no alcanza: falta la foto. Es la regla de la
  mecánica §6: no se acepta una afirmación cuando la política pide un artefacto.
- **El código cuenta, la persona juzga.** Que haya una imagen no dice que la foto muestre el tablero
  terminado; eso lo decide quien aprueba (mecánica §5: la verificación determinista más la persona).
- **Si falta algo, Leda dice qué falta** en palabras de todos los días ("falta una foto del
  tablero") y no pasa la tarea a revisión. Lo calcula el código y la IA lo redacta.

### 6. El aviso a quien aprueba lleva las fotos y el enlace

- **Lo redacta el motor.** Sale con el mecanismo de los avisos guardados como hechos (ADR 0018,
  decisión 8, precisión del 2026-10-05): al llegar su hora, el código relee la tarea y la evidencia
  vigente, la IA redacta desde esos hechos y recién entonces entra a la salida. Reemplaza el texto
  fijo de `_notificar_entrega_al_aprobador`. Es un aviso de coordinación: fuera del tope diario
  (mecánica §10).
- **Las fotos van adjuntas; los demás archivos, en la página.** El aviso dice cuántos hay y cómo se
  llaman. Hasta diez fotos van como álbum.
- **La salida aprende a mandar adjuntos sin atarse más a Telegram.** Una tabla hija de la salida
  (`message_outbox_adjunto`: la fila de salida, el archivo y el orden) apunta a `archivo`, que es del
  dominio, nunca a un identificador de Telegram. El despachador decide cómo mandarlo: reusa el
  identificador que Telegram le dio a ese archivo al recibirlo (es del mismo bot del espacio) y, si no
  sirve, sube la copia propia. No suma columnas a `message_outbox` (riesgo 1 de `docs/STATUS.md`).
- **Orden e idempotencia:** el texto y el álbum son dos filas de una misma respuesta
  (`respuesta_grupo`), y el álbum no sale antes que el texto. Cada fila tiene su clave de
  deduplicación, atada a la entrega. Evidencia nueva sobre una tarea en revisión retira el aviso que
  espera y manda uno nuevo con toda la evidencia vigente, como hoy (ADR 0009, enmienda T6i).
- **El enlace nunca pasa por la IA.** La IA sabe que hay un enlace a la página; el código lo agrega
  al final del texto. La IA no ve ni puede alterar una credencial, y el proveedor de la IA no la
  recibe.
- **El enlace no se guarda en claro en ningún lado.** La fila de salida dice "lleva el enlace de esta
  tarea para esta persona", y el despachador emite el enlace al mandar: la base guarda sólo su hash,
  como el tablero. El registro de turnos guarda el texto sin el enlace.
- **Sin vista previa del enlace:** el mensaje sale con la vista previa desactivada, para que Telegram
  no abra la página por su cuenta.

### 7. La página de la tarea

#### 7a. El enlace

- **Uno por persona y por tarea,** no uno por persona para todas sus tareas: un enlace reenviado
  muestra una sola tarea. Tabla `acceso_tarea`, hermana de `acceso_tablero`: espacio, membresía,
  tarea, hash del token, cuándo se emitió y, si lo hubo, cuándo se revocó. Sin vencimiento
  (decisión 1).
- **Las mismas reglas que el tablero:** se guarda sólo el hash; el espacio y la tarea salen del token,
  nunca de la URL; `leda_app` no tiene privilegios sobre la tabla, sólo `execute` sobre las funciones
  que la emiten y la resuelven (`security definer`, dueño `leda_owner`); un token inexistente,
  revocado o de alguien que ya no puede ver la tarea devuelven la misma página genérica.
- **Qué lo acota, sin vencimiento:** la membresía y el derecho a ver la tarea se revalidan en cada
  pedido; el administrador puede revocar los enlaces de una persona o de una tarea; la página sale
  con `Cache-Control: no-store`, `Referrer-Policy: no-referrer` y `X-Robots-Tag: noindex`.
- **Riesgo aceptado:** un enlace reenviado muestra lo mismo a quien lo reciba, mientras la persona
  original siga pudiendo ver la tarea.
- **Quién lo recibe:** quien aprueba, en el aviso de la entrega; el responsable, en el aviso de un
  pedido de cambios o de la aprobación; cualquiera de los que pueden verla, cuando lo pide por chat
  (una jugada nueva de la lista cerrada, con su ficha).

#### 7b. Quién la ve

- **El responsable, quien la aprueba y el referente del área de la tarea.** Quien la aprueba es el
  aprobador actual del responsable (`membership.aprobador_membership_id`) y también quien haya
  decidido sobre esa tarea antes.
- **El referente del área sí:** conserva la autoridad técnica de su área (constitución §3 y §15) y,
  cuando corresponda, aprueba el componente de su área (mecánica §5). La cadena de aprobación es por
  persona y no por área (Marcos aprueba a Nahuel aunque estén en áreas distintas), así que el
  aprobador no siempre es el referente; sin esta regla, el referente no vería el trabajo técnico de
  su propia área. Necesita que la base sepa quién es el referente de cada área como un dato del
  espacio, no por el nombre de un rol del pack.
- **Nadie más del equipo.** El tablero de hoy le muestra a todo el equipo títulos y estados; la
  página suma fotos, archivos y comentarios de revisión, que son de otra sensibilidad. El seguimiento
  existe para facilitar el trabajo, no para vigilar personas (constitución §8).
- **La autoridad final del espacio** (en CoreWork, Dirección) ve todas las tareas del espacio
  (usuario, 2026-10-07): conserva la decisión final y puede necesitar cualquier evidencia. Es sólo
  lectura, cada vista queda registrada y no recibe un aviso por cada entrega.
- **El administrador de plataforma** ve cualquier tarea del espacio, con un enlace que pide por el
  bot de administración y nunca por el del espacio (constitución §2: el sombrero lo define el
  canal). Ese acceso queda atado a su usuario de plataforma, a una tarea de un espacio, y cada vez
  que mira queda en `audit_log`, como su acceso a las conversaciones (constitución §12). Cuando
  exista el panel de plataforma (ADR 0004), su acceso se muda allá.

#### 7c. Qué muestra

- **La tarea:** título, objetivo, área, responsable, quién aprueba, fecha comprometida, la previsión
  vigente si la hay, criterio de aceptación, qué evidencia pide y qué está cubierto.
- **La historia:** los cambios de estado (de los eventos, con quién y cuándo), las entregas, los
  pedidos de cambios con su comentario, la aprobación, los bloqueos con su causa y las previsiones.
- **La evidencia:** cada pieza con quién la mandó y cuándo; las imágenes se ven en la página, los
  demás archivos se descargan; las retiradas figuran como tales.
- **En palabras de todos los días** (decisión del usuario del 2026-10-07): "esperando aprobación",
  no `en_revision`. Sin identificadores, huellas, nombres de herramientas ni errores técnicos
  (constitución §10). Todo lo que viene de la base se escapa, como en el tablero.
- **No muestra la conversación:** sólo los hechos. Leer lo que alguien escribió en el chat sigue
  siendo un acceso a conversaciones, del administrador y registrado.
- **Sólo lectura.** No tiene botones ni formularios; cambiar algo es de la plataforma (decisión 8).
- **Los archivos se sirven con cuidado:** con el tipo que detectó el código, `nosniff`, descarga como
  adjunto para lo que no es imagen y una política de contenido que no deja ejecutar nada.

#### 7d. El aislamiento lo garantiza la base

- **La página lee sólo por funciones de la base** (`security definer`, dueño `leda_owner`, que no
  saltea la RLS) que reciben el hash del token, fijan el espacio que sale de él, comprueban que la
  persona pueda ver la tarea y devuelven sólo esa tarea. La regla de quién ve qué vive en SQL, no en
  un filtro de Python.
- **Un archivo se pide por la tarea del token.** La función que entrega el contenido exige que la
  evidencia sea de esa tarea: el id de una evidencia de otra tarea, del mismo espacio o de otro,
  devuelve lo mismo que un enlace inválido.
- **Los eventos de estado:** `leda_app` no los lee hoy (sólo los escribe), y así sigue: la historia
  sale de esas funciones.

#### 7e. Registro de quién mira

- **Cada vista y cada descarga quedan registradas** en una tabla propia, de sólo agregar: qué
  acceso, cuándo y qué se sirvió. Sin dirección IP ni navegador. Sirve para detectar un enlace que
  circula; el motor no lo lee y Leda nunca lo usa en la conversación (nada de "Marcos ya vio tu
  foto").
- **Las del administrador van además a `audit_log`** (7b).

### 8. Lo que este ADR no cubre

- **El resto de la plataforma:** el formulario para cargar tareas, cambiar fechas por retrasos,
  gestionar integrantes, aceptar tareas y ver la lista de tareas con su estado (ADR 0017, decisiones
  2, 4 y 5). Va en el ADR de la plataforma, antes de su código.
- **Cómo encaja:** la página es la primera vista de la superficie del cliente (ADR 0004). El ADR de la
  plataforma decide cómo se identifica alguien para escribir (el enlace personal de sólo lectura no
  alcanza para una superficie que escribe en la base), si la página pasa a ser una vista dentro de la
  plataforma y si el enlace por tarea convive con una sesión. Las tablas, las funciones de lectura y
  las pruebas de este ADR quedan como base.
- **Tampoco:** miniaturas o procesamiento de imágenes (suma una dependencia), análisis antivirus,
  cuota de almacenamiento por espacio, evidencia por otro canal que no sea Telegram, ni que la IA
  mire el contenido de una foto.

## Consecuencias

**Migraciones** (desde la `0033`; cada una con su rollback y su ensayo de paridad):

1. **`0033`, la evidencia:** `archivo` y `archivo_de_mensaje`; columnas nuevas en `evidence` (clase,
   texto y archivo); `evidencia_retirada`; las clases que acepta cada tipo de la política; la nueva
   `evidencia_pendiente`; inmutabilidad (privilegios y disparador); el dato de quién es referente
   de cada área.
2. **`0034`, la salida con adjuntos:** `message_outbox_adjunto` y lo que la fila de salida necesita
   para que el despachador emita el enlace al mandar.
3. **`0035`, la página:** `acceso_tarea`, el registro de vistas y las funciones de emisión,
   resolución y lectura.

**Pruebas que tienen que existir en `tests/garantias`:**

- **Aislamiento:** las tablas nuevas en la lista de RLS forzado; un token de un espacio no lee nada
  de otro; el id de una evidencia de otra tarea (mismo espacio u otro) no se sirve; las funciones
  nuevas tienen dueño `leda_owner`.
- **Inmutabilidad:** `update` y `delete` sobre `evidence` y `archivo` fallan para `leda_app`; un
  retiro no borra nada; el `check` de la huella rechaza un contenido que no coincide.
- **Límites:** un archivo por encima del límite vigente y uno fuera de la lista se rechazan; el tipo se juzga por
  el contenido (un ejecutable renombrado `.pdf`, un SVG).
- **Política por tipo:** una frase sola no cubre `foto`; una imagen sola no cubre `explicacion`; lo
  retirado y lo del ciclo anterior no cuentan; aprobar sigue exigiendo la política completa.
- **Alcance de la página:** la ven el responsable, quien aprueba, el referente del área y la autoridad
  final; otro
  integrante, una membresía inactiva y un token revocado reciben la página genérica; el cambio de
  aprobador se refleja en el siguiente pedido.
- **El enlace:** sólo su hash queda en la base; no aparece en el texto que redacta la IA ni en el
  registro de turnos; el mensaje sale sin vista previa; las cabeceras de 7a y 7c están.
- **La salida:** el álbum no sale antes que el texto; repetir el aviso no duplica filas.

Las conversaciones de prueba de la entrega con foto, con álbum, con un archivo fuera de una entrega y
con un archivo demasiado grande van en `tests/conversaciones` (tarea C-2), primero.

**Orden de las porciones:**

1. Recibir y guardar archivos (decisiones 2 a 4, sin evidencia todavía), con sus garantías.
2. La entrega con evidencia y la política por tipo (decisión 5), con la ficha de la entrega (C-3).
3. El aviso redactado por el motor con las fotos (decisión 6), todavía sin enlace:
   `_enlace_portal_tarea` sigue sin inventar ninguna URL (constitución §4).
4. La página y el enlace (decisión 7), que se suma al aviso.
5. El acceso del administrador por el bot de administración.

**Otros documentos que cambian al aceptarlo:** `espacios/corework.yaml` (`almacenamiento` y las clases
de cada tipo), `docs/architecture/frontera.md` (las tablas nuevas y la regla 2), `docs/capacidades.md`
y una nota en el ADR 0009 (el enlace pendiente y las fotos que dejaba fuera).

**Riesgos:**

- **La base crece con los archivos** y el respaldo con ella; la deuda de respaldo y restauración de
  `docs/STATUS.md` pesa más.
- **El webhook atiende de a un mensaje** (deuda registrada): bajar un video grande demora a los
  demás.
- **Un comprimido puede traer cualquier cosa adentro:** Leda no lo abre; quien lo descarga lo abre en
  su máquina, como un adjunto de correo.
- **Una imagen mandada como archivo conserva sus metadatos**, incluida la ubicación; se guarda tal
  cual para que la huella siga valiendo.
- **El reintento del despachador** puede duplicar un álbum si Telegram lo recibió y la respuesta se
  perdió, como ya pasa con el texto.

## Preguntas al usuario

Las cinco del borrador quedaron decididas por el usuario el 2026-10-07 y están en sus decisiones:
la autoridad final ve todas las páginas (7b); un resultado de prueba puede ser texto (5); se aceptan
comprimidos y archivos de proyecto sin abrirlos (2); lo mandado antes de entregar cuenta si se incluye al
confirmar (4); se aceptan videos, con 60 MB de límite y 20 MB mientras no esté el servidor propio (2).
