# ADR 0011: Respuesta inmediata y el indicador de actividad

- **Estado:** aceptada (usuario, 2026-09-27; implementación 2026-09-28)
- **Fecha:** 2026-09-28
- **Alcance:** `src/leda/despachador.py` (`mantener_chat_activo`, borrador
  nativo); `src/leda/gateway.py` (`_despachar_ahora`, `_transporte_de`, el
  llamado a `mantener_chat_activo`); `src/leda/local.py`
  (`Escucha._despachar_ahora`); `tests/test_smoke_runtime.py`,
  `tests/test_gateway.py`, `tests/test_local.py` (nuevo).
- **Evidencia:** `D:\Proyectos\LEDA-PACK-RECONSTRUCCION-20260925\05-TELEGRAM-INDICADOR-Y-ESCRIBIENDO.md`
  (mecanismo recuperado: semilla U+2063, `initial_status_delay_seconds: 1.5`,
  retiro por mensaje transitorio); decisión del usuario, 2026-09-27 (el
  indicador nunca aparece si la respuesta ya está lista); mapa de código de
  sólo lectura de esta unidad (gateway.py:219-221, `despachador.despachar`,
  `ciclo.ejecutar_ciclo_espacio`, `local.Escucha.una_vuelta`).

## Contexto

Dos problemas separados, encontrados juntos por el mismo mapeo:

1. **La respuesta espera más de lo necesario.** Se encola en
   `message_outbox` y sólo sale cuando alguien despacha: en `escuchar`, al
   final de `Escucha.una_vuelta()` (después de procesar TODO el lote de
   `getUpdates` y de sondear el bot de administración); en `servir`, en el
   próximo `Ciclo.tick()`, hasta 20 s después (`ciclo.INTERVALO_SEGUNDOS`).
2. **El indicador de actividad no tiene umbral y se apaga en el momento
   equivocado.** `despachador.mantener_chat_activo` arrancaba
   `sendChatAction(typing)` apenas empezaba a procesarse el turno -- incluso
   para una respuesta que ya estaba lista en milisegundos -- y se apagaba
   cuando `_turno` terminaba de CALCULAR, no cuando la respuesta
   efectivamente salía. No existía ningún borrador nativo (`sendMessageDraft`):
   el pack recuperado documenta que Leda ya lo tuvo, con una semilla
   invisible (U+2063) y un umbral de 1.5 s antes de mostrar nada.

Constitución §10 ya fija el límite: "Mientras procesa, Leda muestra a lo
sumo el indicador de escritura y un estado temporal breve. No muestra pasos
intermedios." Esta unidad no cambia ese límite: lo hace cumplir con un
umbral (nunca destella en una respuesta rápida) y agrega la segunda señal
(el borrador) que el límite ya permitía pero el código no tenía.

## Decisión

### 1. Despacho inmediato, en los dos modos

Apenas se procesa un update con éxito, se despacha la cola `listo` de ESE
espacio, en vez de esperar el resto del lote o el próximo tick.
`despachador.despachar` ya es idempotente y seguro de llamar más de una vez
en paralelo (`for update skip locked`, marca-antes-de-enviar, saludo
reclamado al despachar) -- esta unidad no le cambia una línea; sólo lo llama
más seguido.

**No se engancha adentro de `gateway.procesar_update`.** Se engancha en los
dos puntos de entrada reales:

- la ruta FastAPI `webhook()`, después de `procesar_update(...)`;
- `local.Escucha.recibir()`, después de cada `procesar_update(...)` exitoso
  dentro del lote (no al final del lote).

Los dos resuelven `workspace_id`/`Calendario`/`Transporte` con un helper
propio (`gateway._despachar_ahora`, que cachea un `TransporteTelegram` por
slug igual que `ciclo.Ciclo._transporte_de`; `Escucha._despachar_ahora`, que
reusa `self.transporte`, ya inyectable) y llaman a
`despachador.despachar` una vez. `procesar_update` en sí mismo no cambia: su
contrato sigue siendo "encola, no despacha".

**Por qué no adentro de `procesar_update`:** es la función que comparten el
webhook y el polling (mismo comportamiento en las dos máquinas, por diseño
del módulo), pero también es el punto que ejercitan directamente unas 35
suites de prueba de comportamiento (`test_botones.py`, `test_menu_tarea.py`,
etc., casi todas contra `_turno`) más el corredor de escenarios
`tests/banco/corrida.py` (usado por `test_task_intake.py` y otros), que
corren con un token de bot ficticio (`LEDA_BOT_TOKEN_COREWORK`) y esperan
que `message_outbox` quede en `'listo'`, sin que nada intente hablarle a
Telegram. Despachar ahí adentro habría exigido auditar y potencialmente
tocar cada una de esas suites para evitar una llamada de red real o un
cambio de estado inesperado, por un beneficio de latencia que no es lo que
esas pruebas verifican. Enganchar en los dos wrappers de entrada da el mismo
resultado observable en producción (webhook real, `escuchar` real) con un
radio de cambio acotado a las pruebas que sí ejercitan esos wrappers
(`test_gateway.py`, más `test_local.py`, nuevo).

Una falla al despachar teprano es best-effort y muda: si no se puede
resolver el token, abrir el espacio o llamar a Telegram, se revierte y no se
reintenta ahí mismo -- el tick de fondo (`Ciclo.tick` /
`Escucha.tareas_de_fondo`) sigue siendo la red de contención, y es el que ya
registra un incidente si el envío de verdad se agota
(`despachador._fallo`, `MAX_INTENTOS`). Registrar un incidente aparte acá
sería redundante con ese camino ya existente, por una llamada que es pura
optimización de latencia.

### 2. Indicador diferido: "escribiendo…" + borrador nativo

`mantener_chat_activo` gana un umbral (`umbral`, default **1.5 s para las
dos señales** -- typing y borrador comparten el mismo umbral, por la
decisión del usuario del 2026-09-27, que generaliza el
`initial_status_delay_seconds` del pack recuperado, ahí sólo documentado
para el borrador). Ninguna señal aparece si el bloque `with` termina antes
del umbral. Recién si se cumple:

- se manda **una vez** el borrador nativo (`sendMessageDraft`), sembrado con
  el carácter invisible U+2063 -- nunca texto vacío, aunque la API admita un
  placeholder vacío desde Bot API 10.0: cambiar la semilla es una decisión
  visual aparte, no un reemplazo silencioso (pack 05, hallazgo central);
- se empieza a refrescar `sendChatAction(typing)` cada `intervalo` (4 s por
  defecto, sin cambios respecto de antes).

El borrador **sólo se intenta en chat privado** (`chat_type == "private"`):
Bot API 9.5 (marzo 2026) sólo lo abrió ahí; en grupo o canal se degrada a
sólo "escribiendo…", sin avisar -- mismo criterio que el
`supports_draft_streaming` del código recuperado.

Al salir del bloque `with` -- éxito, excepción, o sin ninguna respuesta
nueva --, si el borrador se llegó a mostrar, se **retira**: la semilla se
manda como mensaje normal silencioso (`disable_notification: true`) y se
borra enseguida por su `message_id` real (`sendMessageDraft` no tiene uno
propio que borrar). Es el mecanismo recuperado del pack 05, sección 5 --
"pausar los frames no alcanza, hay que retirar de verdad antes del
selector".

**El `draft_id` es aleatorio por invocación, no un contador de clase.** El
código recuperado marcaba esto como pendiente ("P": un contador de
proceso no garantiza unicidad entre varios workers). Un entero aleatorio de
31 bits por cada activación de `mantener_chat_activo` cumple "por chat y
turno, nunca reusado" sin ningún estado compartido entre hilos ni procesos
-- más simple que coordinar un contador, y sin su punto débil.

### 3. Por qué se retira al terminar el turno, no al confirmar el envío real

El requisito pide retirar "en el momento en que la respuesta sale (o cuando
el procesamiento termina sin respuesta)". Acoplar el retiro al envío real
habría exigido que `mantener_chat_activo` conociera el `Transporte` y el
resultado de `despachador.despachar` -- mezclando esta unidad con la
decisión 1 y rompiendo el pedido explícito de mantenerlas separables.

Con la decisión 1 en el mismo espacio, el hueco entre "`_turno` termina" y
"la respuesta se despacha" es, en el camino feliz, el tiempo de UNA llamada
a `despachar()` -- milisegundos, no los 20 s de antes. Retirar al terminar
`_turno` (como ya hacía `mantener_chat_activo`, que nunca supo de despacho)
es indistinguible en la práctica de retirar al enviar, para cualquier
respuesta sin botones. Para una respuesta CON botones -- el caso que el pack
marca como el difícil --, retirar acá es estrictamente más seguro: pase lo
que pase con el despacho después (que corre fuera de este bloque, en el
llamador), el borrador ya no existe cuando los botones puedan aparecer,
sin depender de que el despacho ocurra rápido.

### 4. Excepción acotada a "todo lo visible sale por la cola"

`nucleo/mecanica-pm.md` §12 y la regla del proyecto dicen que Leda nunca
le habla a Telegram directamente; todo pasa por `message_outbox`. El typing
y `acusar_toque` ya eran la excepción documentada (comentario de
`acusar_toque`, arriba en este archivo); el borrador se suma a esa MISMA
excepción, con el mismo argumento: no lleva contenido (la semilla es
invisible), es transitorio (se retira antes de cualquier respuesta real),
nunca cuenta contra el tope diario de mensajes automáticos (no pasa por
`message_outbox`, así que `despachador._ya_recibio` ni lo ve), y nunca
sustituye ni duplica la respuesta real -- que sigue saliendo, siempre, por
la cola. `docs/architecture/frontera.md` no enumera esta excepción hoy (sólo
describe la frontera núcleo/adaptador), así que esta ADR no lo toca.

### 5. Política de fallas (enmendada tras revisión del padre, 2026-09-28)

Una falla al mandar typing, el borrador o al retirarlo nunca es fatal
(Constitución §10): nunca bloquea ni duplica la respuesta real. Pero "no
fatal" no es "en silencio" -- la primera versión de esta ADR descartaba las
tres en silencio, y la revisión del padre marcó que eso viola la regla del
proyecto sin necesidad: no cuesta nada hacerlas visibles sin inundar.

- **Se imprime, a lo sumo una vez por tipo (`typing`/`borrador`/`retiro`) y
  por invocación de `mantener_chat_activo` -- es decir, por turno.** El
  refresco de typing reintenta cada `intervalo` (4 s); sin este tope
  imprimiría en cada reintento. Sólo el tipo y el estado HTTP si lo hay
  (`despachador.texto_error_seguro`) -- nunca texto crudo, URL ni token.
  `_reportar_falla_indicador` lleva la cuenta, local a cada invocación.
- **Una falla al RETIRAR pesa más que las otras dos: el borrador puede
  quedar visible para la persona**, no sólo un typing que dejó de
  refrescarse. Además del print (uno por turno, igual que las otras), se
  registra un incidente -- `_reportar_falla_retiro`, mismo patrón que
  `saludo.reportar_falla`/`ciclo.SupresorDeRepetidos`: deduplicado por
  `(workspace_id, 'retiro_borrador')` mientras el proceso siga vivo, no uno
  por turno. Necesita el `cur` de la transacción que ya procesa el turno
  -- `gateway.procesar_update` se lo pasa (`cur`, `workspace_id`, ya en su
  alcance); sin `cur` (otro llamador, o una prueba sin base) sólo imprime.
- La limpieza cosmética de `_close_client_bounded` (cerrar un cliente
  propio cuando el hilo no llegó a arrancar) sigue en silencio: no es una
  falla de comunicación con Telegram, es liberar un recurso propio, y
  duplicarla con un print no aporta nada que el administrador pueda usar.
- Registrar un incidente por CADA typing o borrador fallido (no sólo el
  retiro) seguiría inundando la bandeja del administrador con ruido
  cosmético sin ganancia -- esa parte de la decisión original se mantiene;
  lo que cambió es que ahora, además del incidente acotado al retiro, las
  tres fallas quedan visibles en la consola del proceso.

## Alternativas consideradas

- **Enganchar el despacho inmediato adentro de `procesar_update`.**
  Rechazada por el radio de cambio sobre pruebas de comportamiento que no
  tienen nada que ver con latencia de transporte (arriba, decisión 1).
- **Acoplar el retiro del borrador al resultado de `despachador.despachar`.**
  Rechazada: rompe la separabilidad pedida entre las dos unidades, y la
  decisión 1 ya vuelve la diferencia práctica insignificante (arriba,
  decisión 3).
- **Mantener el contador de clase del código recuperado para `draft_id`.**
  Rechazada: es el punto débil que el propio pack marcaba como pendiente
  (sin garantía entre procesos). Un id aleatorio por invocación cumple el
  mismo contrato ("nunca reusar un draft retirado", "por chat y turno") sin
  ningún estado compartido.
- **`disable_notification: false` en el mensaje transitorio de retiro,
  igual que el código recuperado.** Rechazada: el propio pack 05 marca este
  punto como no verificado ("si el adaptador interpreta notificaciones de
  otro modo puede haber efectos visuales/sonoros"). Un mensaje que se borra
  al instante no tiene por qué sonar o vibrar en el teléfono de nadie;
  silencioso es el default más seguro para Leda, que ya evita interrumpir
  fuera de horario.

## Consecuencias

- `message_outbox` puede quedar en `'enviado'` -- no `'listo'` -- apenas
  vuelve una respuesta por el webhook o por `escuchar`, cuando antes
  quedaba siempre `'listo'` hasta el próximo tick. Cambio de comportamiento
  observable: `tests/test_gateway.py` se actualiza en consecuencia.
- `mantener_chat_activo` gana `chat_type` (para decidir si intenta el
  borrador) y `umbral`; las pruebas de `tests/test_smoke_runtime.py` que
  ejercitan su hilo de refresco pasan `umbral=0` explícito para seguir
  probando el refresco y la limpieza sin esperar el umbral por defecto --
  eso queda cubierto por pruebas nuevas dedicadas al umbral.
- `mantener_chat_activo` gana `cur`/`workspace_id` (opcionales, sólo para el
  incidente de una falla al retirar); `gateway.procesar_update` le pasa el
  mismo `cur`/`workspace_id` que ya usa para el turno. Un incidente nuevo,
  `etapa='indicador_actividad'`, puede aparecer en `python -m leda
  incidentes <espacio>` -- sólo por una falla al RETIRAR el borrador, nunca
  por typing ni por mandarlo, y deduplicado por proceso.
- **Pendiente, fuera de esta unidad:** renovar el borrador más allá de sus
  ~30 s de vigencia nativa para un turno excepcionalmente largo -- el pack
  recuperado ya lo marcaba como no probado ("probar explícitamente
  expiración/renovación del draft"); esta unidad sólo manda la semilla una
  vez por activación, igual que el requisito pedía ("Refresh typing at most
  every 4 s" -- nunca menciona refrescar el borrador).
  Una prueba visual real contra Telegram (batería mínima del pack 05, § 10)
  queda pendiente de una sesión progresiva por Telegram real, fuera del
  alcance de esta unidad (sólo pruebas deterministas, sin llamadas de red).

## Enmienda (2026-09-28): revisión de confiabilidad sobre el commit `e2a094e`

Task #9b, sobre los hallazgos R3-001 a R3-005 de la revisión del padre. Tres
correcciones de comportamiento, dos de prueba.

### R3-001 -- el retiro nunca puede llegar antes que el propio borrador

El hilo de `mantener_chat_activo` marca `activado` **antes** de llamar a
`sendMessageDraft` (para que un turno rapidísimo nunca cuente como
"activado" a medias). Pero el `finally` del bloque `with` sólo esperaba
`espera_cierre` (0.25 s por defecto) a que el hilo entero terminara, y
después miraba `activado` sin más: si el turno terminaba justo cuando el
hilo recién había arrancado esa llamada, y era lenta, retirar de inmediato
podía llegar a Telegram **antes** que el propio borrador -- exactamente el
riesgo que la decisión 3 original quería evitar.

Corrección: un evento nuevo, `borrador_intentado`, que el hilo marca
apenas ese intento (éxito o falla) termina. Antes de retirar, el `finally`
espera ese evento, acotado a `timeout_borrador` (nuevo parámetro, por
defecto el mismo timeout que ya tiene el cliente HTTP propio, 5 s) --
nunca más de lo que esa llamada puede tardar en resolverse sola. Si
resuelve a tiempo, retira; si no (un cliente colgado más allá de su propio
timeout, un caso ya patológico), abandona el retiro en vez de arriesgar el
orden, y lo reporta como una falla de "retiro" más (print + incidente,
sección "Política de fallas").

**Trade-off, reportado en vez de decidido en silencio:** en el peor caso
(Telegram lento justo en ese instante), esta espera puede sumarle hasta
`timeout_borrador` a lo que tarda `mantener_chat_activo` en salir -- y
como el despacho de la respuesta real corre DESPUÉS de este bloque
(`gateway._despachar_ahora_en_fondo` ya corre en su propia tarea de fondo,
pero recién se agenda cuando `_turno` retorna), esa espera retrasa el
momento en que la respuesta queda agendada para despacharse. Es acotado
(nunca más que una llamada HTTP), y sólo se paga en el camino ya lento
(Telegram tardando en responder DE TODAS FORMAS) -- pero es un retraso
real, no cero, y se documenta acá en vez de asumir que "esperar un poco
más" no tiene costo.

### R3-002 -- una falla al registrar el incidente del retiro no puede abortar el turno

`_reportar_falla_retiro` llamaba a `registrar_incidente` directo sobre el
cursor del turno, sin aislar. Un error SQL real ahí (no sólo una excepción
de Python) deja la transacción de PostgreSQL abortada; cualquier
`insert`/`update` posterior en la MISMA transacción -- incluida la
respuesta que el turno ya encoló -- se pierde al llegar al `commit`, por un
incidente que ni siquiera es sobre ella.

Corrección: el mismo patrón que ya usa `_reportar_falla_saludo_aislada` --
el `insert` corre adentro de `with cur.connection.transaction():` (un
SAVEPOINT). Si falla, se revierte sólo ese SAVEPOINT; el resto de la
transacción sigue sirviendo.

### R3-003 -- el despacho inmediato no puede bloquear el bucle de eventos de `servir`

`webhook()` es `async def`, pero llamaba a `_despachar_ahora` -- síncrono,
puede hacer un `POST` real a Telegram -- en línea, antes del `return`. Un
envío lento bloqueaba el bucle de eventos entero (nada más se atendía
mientras tanto) y corría el riesgo de que Telegram reintente la entrega
del update por no recibir el ACK a tiempo.

Corrección: `webhook()` agenda `_despachar_ahora_en_fondo` como
`BackgroundTasks` de FastAPI en vez de llamarla en línea -- corre después
de mandar la respuesta, en su propio hilo (`anyio.to_thread.run_sync`).
Esa función abre su PROPIA conexión (`conectar()`, nunca la `_conn()`
cacheada que usa el resto del pedido: una conexión de psycopg no es segura
de usar desde dos hilos a la vez) y la cierra siempre al terminar --
**trade-off deliberado**: una conexión nueva por despacho de fondo, en vez
de una agrupada/reusada, a cambio de eliminar por completo el riesgo de
que dos hilos compartan una. Sigue siendo best-effort y no en silencio
(`texto_error_seguro`, sin incidente propio -- redundante con el que ya
deja el tick de fondo si el envío de verdad se agota).

`TestClient` no sirve para probar esto (verificado empíricamente: espera a
que las tareas de fondo terminen antes de que `.post()` devuelva) --
`tests/test_gateway.py` llama a la función de la ruta directamente, con un
`BackgroundTasks` real, para comprobar que nada corrió todavía cuando la
respuesta ya está lista.

Por esto, `tests/conftest.py` deshabilita `gateway.conectar` por defecto
además de `gateway._transporte_de` -- mismo criterio, mismo riesgo (una
conexión real contra lo que sea que `config.db_url` resuelva en el
entorno de pruebas).

### R3-004/R3-005 -- pruebas deterministas del indicador

`tests/test_smoke_runtime.py`: los `sleep` fijos alrededor del borrador se
reemplazan por esperas sobre eventos (`_ClienteIndicador.esperar`, uno por
endpoint, marcado apenas se intenta esa llamada -- éxito o falla). Indexar
`http.urls(...)​[0]` ahora siempre va después de un `assert len(...) == 1`.
La prueba de "falla al mandar y retirar" pasa a comprobar, además de que
el turno no se rompe, que las dos llamadas se intentaron de verdad (una
vez cada una) y que cada una imprimió exactamente una línea.
