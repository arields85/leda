# Pendientes para la plataforma

> **Nota del 2026-10-04.** La rama `feat/flujo-de-un-mensaje` quedó congelada. Las filas que dicen
> "por construir" o "construido" en esa rama, y las que nombran ajustes del alta por chat (`alta`,
> `redaccion`, `stream`, `horizonte_tarea`, los topes por modelo), describen el flujo C: nada de eso
> se construye ni se retoma ahí. Lo que siga haciendo falta se vuelve a plantear en el Motor, con el
> diseño del motor de conversación (ADR 0018) y con el alcance (ADR 0017); ver [`../STATUS.md`](../STATUS.md).
> El inventario se conserva porque las necesidades de configuración siguen valiendo.

Lista viva de lo que la plataforma de administración tiene que permitir configurar o
hacer cuando se construya. Existe para que, el día que se empiece, no haya que
reconstruir de memoria qué se fijó por consola, por SQL o en el pack mientras tanto
(pedido del usuario, 2026-10-01). La unidad de entrega es
["Panel de plataforma"](../ROADMAP.md#panel-de-plataforma), en el roadmap; este documento
es su inventario.

**Cómo se mantiene:** cada vez que algo se decide como "configurable desde la
plataforma" o se fija a mano (pack, SQL, consola) porque la plataforma no existe, se
agrega acá con dónde vive hoy.

**Primera versión y segunda** ([ADR 0022](../decisions/0022-plataforma-web-de-tareas.md), aceptado el
2026-10-12). La primera versión hace cuatro cosas: la lista de tareas por puesto, el formulario de
carga con sus controles, el cambio de fecha con el pedido de más tiempo y el alta y la baja de
integrantes; también muestra los apodos (ADR 0020). Todo lo demás de este inventario (horarios,
feriados, cadencias, tono, márgenes, modelos de IA y el resto de la configuración) sigue en el
paquete del espacio y la consola hasta la segunda versión.

## Reglas que la plataforma no puede saltear

- **Dos firmas para ampliar autoridad** ([constitución](../../nucleo/constitucion.md) §2):
  la autoridad del espacio decide qué, el administrador de plataforma lo aplica. Las dos
  quedan registradas.
- **El núcleo no se configura** (constitución §14): ningún ajuste puede desactivar una
  regla del núcleo, la confirmación humana de §7, la auditoría ni el aislamiento entre
  espacios.
- **Todo cambio queda auditado**, con quién, cuándo, el valor anterior y el nuevo.
- **Un valor inválido nunca falla en silencio:** se usa el valor por omisión y queda un
  incidente (el patrón ya implementado para `alta`, `redaccion` y `horizonte_tarea`).
- **Una tarea no vence en un día no hábil** (usuario, 2026-10-10; `odd/tasks/fase-c.md`,
  decisión 56): el formulario no acepta una fecha objetivo, ni un cambio de fecha, que caiga
  sábado, domingo o feriado del calendario del espacio, y pide un día hábil. Si una entra por
  otro lado, la escalera la cuenta como si venciera el día hábil anterior.
- **Los valores no fijan el comportamiento:** topes, márgenes y fechas son datos del
  cliente; Leda no se ajusta a sus valores actuales (decisión del usuario, 2026-10-01).

## Acceso y operación

| Qué | Hoy | Referencia |
|---|---|---|
| Autenticación de quien opera Leda | No existe; decisión abierta (el enlace por Telegram no sirve: autentica contra una membresía) | ROADMAP, "Panel de plataforma" |
| Alta de un espacio (la entrevista de `nucleo/alta-de-equipo.md`) y su activación | Pack YAML a mano + `python -m leda importar <espacio> --activar` | `nucleo/alta-de-equipo.md` |
| Enlaces de activación individuales, entregados uno a uno | `python -m leda enlaces <espacio> --solo <nombres>` | alta de equipo, bloque 8 |
| Ver incidentes: dónde falla y qué lo hizo fallar, con acceso a la conversación que lo causó | `python -m leda incidentes <espacio>` | ROADMAP, "Panel de plataforma" |
| Respaldo, restauración y migraciones | Consola y `db/respaldos/` | constitución §2 |
| Dónde corre: Leda y la plataforma van en un VPS (usuario, 2026-10-08) | Hoy, la PC del usuario; las pruebas del enlace a la página de la tarea, con `LEDA_BASE_URL=http://localhost:8000` y Telegram en la misma PC | Hace falta, antes de subir: dominio con HTTPS (la dirección del enlace), secretos fuera del repositorio, respaldo y restauración, el webhook atendiendo más de un mensaje a la vez, registros sin datos sensibles. Subir es una operación remota: la autoriza el usuario, con su plan |

## Configuración global

| Qué | Hoy | Referencia |
|---|---|---|
| Proveedor y modelo de lenguaje, con el cambio atribuido | `python -m leda modelo <id> --proveedor <p>` (escribe `model_config`) | ROADMAP, "Panel de plataforma" |
| Dónde vive la clave de cada proveedor | Una sola `LEDA_LLM_API_KEY` en `.env`, leída al arrancar | `PENDIENTE` |
| Modelo por espacio (`model_config` ya lo admite) | Sin superficie | `PENDIENTE` |
| **Importante (pedido del usuario, 2026-10-03).** Elegir el modelo y fijar el tope de salida de cada modelo (`tope_conduccion` para el alta, `tope_ruteo` para el ruteo), para los modelos que razonan por dentro antes de responder | A mano en `model_config.parametros` (rama `feat/flujo-de-un-mensaje`); Gemini 3.8 flash: 4000 y 3000; sin valor, 700 y 512 | Hallazgo del 2026-10-03: con el tope fijo de 700, Gemini gastaba todo en razonar y no respondía. Más tope permite razonar más y puede costar latencia: medirlo por modelo (tarea 0-24 de la rama de flujo) |
| Servicio que transcribe los mensajes de voz y dónde vive su clave | No existe: los audios no se transcriben | ROADMAP, "Mensajes de voz" (pedido del usuario, 2026-10-02) |
| Plazo total de un turno del modelo: cuánto se espera al proveedor antes de dar el turno por fallido (aviso a la persona e incidente) | Por construir en la rama `feat/flujo-de-un-mensaje`: valor fijo de 2 minutos | Decisión del usuario (2026-10-02), a partir del turno del alta que quedó colgado sin fin. Tiene que poder ajustarse desde la plataforma |
| Qué hace Leda cuando la IA no responde al redactar un aviso para otra persona (por ejemplo, el pedido de confirmación a quien aprueba): reintentar más tarde, mandar sólo la lista de datos o avisar la falla sin enviar | Construido en la rama `feat/flujo-de-un-mensaje` (P-1b, ADR 0016): reintentar más tarde con espera creciente (1, 2, 4 y 8 minutos); al quinto intento fallido el aviso queda `fallido` y ya no se reintenta, con incidente y aviso de falla a quien pidió (pendiente de decidir con el usuario si debería seguir reintentando) | Decisión del usuario (2026-10-03): por ahora reintentar; tiene que poder elegirse desde la plataforma |
| Cuánto se espera a que vuelva el proveedor del modelo antes de avisar a la persona que no se pudo y pedirle que lo escriba de nuevo | Por construir en la rama `feat/flujo-de-un-mensaje`: 4 horas hábiles; el sondeo del proveedor empieza a los 30 s y se espacia | Decisión del usuario (2026-10-02), tareas P4 a P6 de esa rama |

## La jerarquía, los avisos de cada uno y la vista de todo (usuario, 2026-10-09)

- **La jerarquía se arma desde la plataforma:** quién está a cargo de qué sector, quién
  aprueba el trabajo de quién. Hoy sale del pack (`areas[].referente`, `aprobado_por`). Rige
  la decisión 28 de `odd/tasks/fase-c.md`: quién revisa depende de quién era la tarea; a la
  autoridad final (Ismael) le llegan para aprobar sólo las tareas de los encargados de sector.
  Cambiar el encargado de un sector es un solo paso, sin un rato sin encargado: un sector sin
  encargado termina los pedidos del detalle que esperaban su decisión (decisión 33; 2026-10-10).
- **Qué avisos le llegan a cada persona se elige desde la plataforma.** Ejemplo: Ismael elige si
  le llega un aviso cuando Nahuel termina una tarea, o ninguno. Lo que la persona necesita para
  trabajar (pedidos de su decisión, la confirmación de lo suyo) no se apaga: se eligen los
  avisos informativos.
- **La autoridad final ve todo el seguimiento desde la plataforma**, sin que Leda le avise ni le
  pida nada: qué está haciendo cada uno, sus tareas, fechas, bloqueos y entregas. Hoy ya puede
  abrir la página de cualquier tarea (`puede_ver_tarea`, ADR 0019); falta la vista de todo junto.

## Configuración de cada espacio

Lo que hoy sale del pack (`espacios/<espacio>.yaml`, se cambia editando y reimportando) o
de `workspace_setting` (se cambia por SQL).

| Qué | Hoy | Notas |
|---|---|---|
| Identidad, glosario, vocabulario y niveles (`espacio`, `glosario`, `niveles`) | Pack | Nombres visibles de cada nivel de trabajo (mecánica §1) |
| Integrantes y roles: alta y baja de personas, su área, su rol, a quién aprueban y quién las aprueba, ausencias (`areas`, `roles`, `personas`) | Pack, reimportando | Pedido del usuario (2026-10-01). Quién aprueba a quién (`aprobado_por`) define el botón Confirmar o Enviar a aprobación. Una baja no puede dejar tareas sin responsable ni un área sin aprobador (validaciones de `nucleo/alta-de-equipo.md`) |
| Política de aprobación (`aprobacion`) | Pack | Pendiente: quién aprueba una excepción cuando quien pide ya es el aprobador ("Trabajo que no entra en una tarea") |
| Evidencia por área (`evidencia`) | Pack | Hoy se muestra con claves internas ("explicacion"): falta su nombre legible |
| Horario laboral del equipo, horarios distintos por persona y feriados (`calendario`) | Pack + `python -m leda feriados <espacio>` | Pedido del usuario (2026-10-01): define cuándo salen los avisos. CoreWork, 09:00-17:00. Fuera de horario Leda no escribe (constitución §8): un aviso de las 18 sale a las 9 del día siguiente. Horario por persona: alta de equipo, bloque 2, pregunta 6. Urgencia fuera de horario sólo por regla aprobada (mecánica §11). Incluir la opción **sin restricción horaria** (todos los días, todo el día), para que un cliente pueda recibir mensajes a cualquier hora (decisión del usuario, 2026-10-02); hoy se hace en desarrollo con `tools/restriccion_horario.py` |
| Cadencias: qué pide Leda, qué días y a qué hora (estado, resumen grupal, cierre semanal, informe), y la reunión periódica a preparar (`cadencia`, `reunion_periodica`) | Pack → `cadence_job` (se cambia reimportando el pack; `activo` y el cron, por SQL). Desde la C-6 (`leda.motor.cadencias`) las cadencias a cada integrante en privado corren en el motor: el pedido de estado de cada persona con la lista de sus tareas, a la hora de la cadencia o a las 10:00 si es antes (la hora en que Leda manda lo suyo). Las del grupo también: el informe al grupo del espacio (`leda.motor.informe_al_grupo`), a la misma hora, que sale siempre y repite lo que sigue igual (decisiones 25, 54 y 55; `odd/tasks/fase-c.md`, C-6) | Pedido del usuario (2026-10-01). Una cadencia fuera del horario declarado advierte al configurarla (alta de equipo, "Advierten, pero no impiden"); en el motor, una que cae fuera del horario no sale ese día y queda omitida. Pedido del usuario (2026-10-08): activar y desactivar cada cadencia, y cambiar su frecuencia y su horario desde la plataforma, porque junto con el seguimiento de cada tarea pueden ser demasiadas |
| Cuántos días hábiles antes del vencimiento sale el aviso previo de una tarea (un solo aviso; no pide respuesta) | Fijo en el código: un día hábil (`escalera.py`, el paso `-1` de la escalera). En el Motor pasa al pack y después a la plataforma | Decisión del usuario (2026-10-04; ADR 0018, decisión 9b, que enmienda el ADR 0017, decisión 3b): CoreWork, tres días hábiles; mínimo, un día hábil (mecánica §9 permite alargar los intervalos, nunca acortarlos por debajo de un día hábil). Una tarea creada con menos días por delante comprime la escalera |
| A qué hora salen los mensajes que Leda manda por su cuenta (aviso previo, pedidos de estado, repreguntas, escalamientos, avisos guardados) | Fijo en la prueba chica: 10:00 (`HORA_DE_SALIDA`, `prueba_chica/tiempo.py`), dentro del horario del espacio | Una sola hora para todo lo que Leda inicia, para que lo que promete ("mañana a las 10 te vuelvo a preguntar") sea la hora real (2026-10-06). En el producto, un valor de cada espacio que se elige en la plataforma y usan todos, también las cadencias, que hoy traen su propia hora en el pack (usuario, 2026-10-09, decisión 45) |
| Límites de contacto (`limites_de_contacto`) | Pack → `workspace_setting['limites_de_contacto']` | Los avisos de coordinación quedan fuera del tope (mecánica §10) |
| Margen para corregir: cuánto espera el aviso a otra persona que sale de algo que alguien dijo, para que quien habló pueda corregirse (`margen_para_corregir_minutos`) | `workspace_setting` por SQL, 10 minutos por omisión (`motor/margen.py`); el importador del pack no lo carga | Pedido del usuario (2026-10-08): tiene que poder ajustarse desde la plataforma. Los avisos de una decisión (aprobada, cambios pedidos) salen sin margen (`odd/tasks/fase-c.md`, decisión 8 del 2026-10-08) |
| Cuánto vale un motivo ya dado para una fecha nueva de la misma tarea (`motivo_vale_minutos`) | `workspace_setting` por SQL, 60 minutos por omisión (`motor/fichas.py`) | Mismo caso que el margen: un tiempo de la conversación que hoy no se ajusta sin SQL |
| Cuánto espera un aviso mientras la persona está conversando con Leda (`no_interrumpir_minutos`) | `workspace_setting` por SQL, 30 minutos por omisión, decisión del usuario (2026-10-08; conversación 26, `motor/no_interrumpir.py`, C-3d, D5); el importador del pack no lo carga | Va en `workspace_setting`, como el margen, y se ajusta desde la plataforma |
| Cuánto espera una pregunta de Leda sin contestar antes de repetirse, y después de la repetición antes de que salga aparte el tema siguiente (`pregunta_sin_contestar_minutos`) | `workspace_setting` por SQL, 240 minutos (4 horas) por omisión, decisión 21 del usuario (2026-10-08; conversación 30, `motor/pregunta_sin_contestar.py`, C-3d, D5b); el importador del pack no lo carga | Pedido del usuario (2026-10-08): ajustable desde la plataforma. Va en `workspace_setting`, como el margen y la espera de la conversación |
| A los cuántos días hábiles un bloqueo abierto se le informa al referente aunque la cadena se mueva (`bloqueos.escala_solo_a_los_dias`) | Pack (`espacios/corework.yaml`), 5 días hábiles en CoreWork; se cambia reimportando el pack. Sin el ajuste, o con uno que no es un número entero de días, 1 o más, vale el del producto, 5 (`leda.motor.bloqueo_viejo`, C-5, porción 5) | Decisión del usuario (2026-10-08, Fase C, pregunta 7): se informa siempre, una vez, con toda la historia; ajustable desde la plataforma |
| Cuánto espera Leda una pregunta suya sin contestar antes de volver a mandarla el mismo día | `PENDIENTE` de construir; propuesta del usuario (2026-10-08): 4 horas | Pedido del usuario (2026-10-08): tiene que poder ajustarse desde la plataforma. La regla completa está en discusión (`odd/tasks/fase-c.md`, D5) |
| Tiempos de respuesta, urgencia, escalamiento, bloqueos (`tiempos_de_respuesta`, `urgencia`, `escalamiento`, `bloqueos`) | Pack (`bloqueos` → `workspace_setting`) | |
| Tono y conversación (`persona`, `conversacion`): cómo trata Leda a las personas del cliente (`registro`: vos o usted), si usa emojis, formalidad y largo de las respuestas | Pack → `persona_config`; CoreWork: `registro: vos`, `emojis: true` (cambiado el 2026-10-02) | Decisión del usuario (2026-10-02): se configura desde la plataforma. Desde C0-13 (rama de flujo) el código toma el tono del pack en el alta y en la redacción; nunca va escrito en el código |
| Bot y grupo de Telegram (`telegram`) | Pack + secreto en `.env` | El grupo de gestión de CoreWork no existe ("chat not found", STATUS) |
| Objetivos y sus fechas (`objetivo_inicial`, frentes) | Pack | Hoy ningún objetivo tiene fecha: `horizonte_meses: 12` no se convierte al importar |
| Margen máximo de la fecha de una tarea (`horizonte_tarea`, 2 meses, tope 120) | Pack → `workspace_setting` (rama `feat/flujo-de-un-mensaje`) | Regla de fondo decidida: la fecha de una tarea no pasa la de su objetivo; el margen es la red de seguridad |
| Modo del alta (`alta`: `guiada` o `conversada`) | `workspace_setting` por SQL (rama `feat/flujo-de-un-mensaje`) | Experimento del ADR 0014; se retira cuando el alta conversada se adopte |
| Cómo se ve Leda mientras responde: el stream (encendido o apagado, y su modo: real, que muestra el texto mientras el modelo escribe, o progresivo después de verificar), el indicador "escribiendo…" animado (umbral antes de mostrarlo, cada cuánto se renueva) y el borrador nativo de Telegram | `stream` en `workspace_setting` por SQL (rama `feat/flujo-de-un-mensaje`): `true`, `{"activo": true}` o `false`; ausente, apagado; inválido, apagado con incidente `interruptor_stream`; el indicador, con valores fijos en `despachador.mantener_chat_activo` (aparece a los 1,5 s, se renueva cada 3 s) | Pedido del usuario (2026-10-01). Experimento: sólo alta conversada y chat privado; el modo real muestra texto todavía sin verificar. Pendiente comparar los dos modos de stream en real, con el trabajo de latencia (ADR 0011) |
| Variante de redacción (`redaccion`: A o B) | `workspace_setting`, sembrado por el importador | Experimento del ADR 0014 |
| Apodos de los integrantes: ver los que Leda aprendió (con quién lo enseñó y cuándo), agregarlos, cambiarlos y borrarlos | `PENDIENTE` de construir (ADR 0020, aceptado el 2026-10-11) | Decisión del usuario: Leda los aprende por chat con confirmación de una persona, una persona puede tener varios, y por chat los sigue aprendiendo y corrigiendo aunque existan en la plataforma. Cada cambio se audita con su canal |
| Retención y visibilidad de las conversaciones | Fijado para el piloto por el ADR 0002 | Pasa a ser del cliente; requiere un ADR nuevo |
| Revisión periódica del pack (cada N meses) | No existe | `nucleo/alta-de-equipo.md`, "Revisión periódica" |
| Quién deja de compartir el detalle de una tarea y desde dónde, y si lo compartido vence solo (por ejemplo, cuando la tarea se cierra) | No hay jugada por chat ni comando: sólo la operación de la cocina `dejar_de_compartir_tarea`, que puede usar el encargado del sector de la tarea o quien la compartió (auditada; corta también el enlace ya emitido). Lo compartido no vence: vale hasta que alguien lo revoca | Decisión 33 del usuario (2026-10-09; `odd/tasks/fase-c.md`, "El resumen para cualquiera, el detalle a pedido"). `PENDIENTE` con el usuario: si se revoca desde la plataforma, por chat o también por quien lo recibió, y si vence al cerrarse la tarea |

## La puerta del equipo, porción 1 (2026-10-12)

Construida en la rama `feat/plataforma` ([`../capacidades.md`](../capacidades.md), "Lo que agregó la
plataforma web"); plan y evidencia en
[`../../odd/tasks/plataforma-p1.md`](../../odd/tasks/plataforma-p1.md).

**Valores fijados a mano en esta porción:**

| Qué | Hoy | Notas |
|---|---|---|
| Nombre y duración de la cookie de la sesión | `leda_sesion`, `Max-Age` de 400 días (lo más que aceptan los navegadores), renovada cada vez que la web pregunta quién es la persona; `web_app.py` (`COOKIE`, `DURACION_DE_LA_COOKIE_S`) | La sesión de la base no vence (decisión 4); la cookie sólo la transporta. Cada puerta tendrá su cookie (decisión 12) |
| Vencimiento del enlace de entrada | Ninguno por tiempo, como el de la página de la tarea (migración `0057`): deja de servir al canjearse, al emitirse otro o al cortarse las sesiones | El ADR 0022 no fija un plazo |
| Profundidad de la cadena de esperas | Hasta 10 niveles, sin repetir (migración `0059`) | |
| Qué estado muestra una tarjeta cuando tiene más de uno | Trabada y vencida juntas ("[TRABADA] [VENCIDA]"); entregada o en curso, sólo sin ninguna de ellas (`web_app._marcas`). El panel cuenta una tarea trabada y vencida en los dos números | Decisión 5 del usuario (2026-10-12) |
| Cuánto atrás muestra las terminadas | 30 días corridos desde el reloj de Leda, por el evento que terminó la tarea (migración `0060`, `terminadas_que_ve`) | Decisión 3 del usuario (2026-10-12): "las tareas suelen ser largas; una semana se queda corta" |
| Usuario público del bot del equipo, para el botón "> consultar a leda" | Pack, `telegram.bot_usuario` (sin "@"; opcional), que el importador guarda en `workspace_setting` (`bot_usuario`; la base exige un usuario de Telegram válido). CoreWork: `PENDIENTE` del usuario (en `espacios/corework.yaml`, comentado); sin él, la web no muestra el botón | Decisión 8 del usuario (2026-10-12). No es un secreto (el token sí, y sigue en `.env`). Hoy la consola lo obtiene de Telegram con el token (`getMe`, en `leda enlaces`) |
| Colores, letras y medidas del aspecto | En el tema de Tailwind (`web/src/index.css`): los cuatro colores de estado, los grises, JetBrains Mono, tamaños, bordes y sombras | Decisión 18. Las dos páginas sin la web (el botón "Entrar" y la de un enlace que no sirve) repiten los colores a mano en `web_app.py` |

**Abierto:**

- **Las ocho preguntas de la noche, decididas por el usuario el 2026-10-12** y construidas en la
  P1-6 (`odd/tasks/plataforma-p1.md`, "Decidido por el usuario"): de una tarea ajena, lo mismo que
  el informe al grupo (trabada, su cadena, y vencida recién con el atraso hablado, con la
  previsión); las terminadas de 30 días; el botón "> consultar a leda" con el bot del equipo. Falta
  que el usuario declare el usuario del bot de CoreWork en el pack.
- **Técnico:**
  - dos toques seguidos en "Entrar" pueden terminar en "Este enlace ya no sirve" aunque el primero
    haya abierto la sesión;
  - la tarjeta de una tarea entregada no dice quién la revisa;
  - la tarjeta no abre la página de la tarea, aunque la API dice si la persona la puede ver;
  - las advertencias de las revisiones listadas en `odd/tasks/plataforma-p1.md` ("Progreso y
    evidencia"): dos emisiones simultáneas del enlace de una persona hacen fallar la segunda; un enlace
    sin canjear de alguien que dejó el equipo vuelve a servir si lo reincorporan; una espera por el
    bloqueo de quien destraba sigue contando aunque ese bloqueo ya se haya resuelto; `vencida` no mira
    una nueva previsión de la persona (el motor sí); los días que quedan cuando vence el mismo día; el
    candado global atiende la web de a un pedido; el chequeo de `Origin` detrás de un proxy.

## Decisiones abiertas que la plataforma va a necesitar

- Cómo se autentica quien opera Leda.
- Si el tablero de cada cliente muestra sus propios incidentes o sólo el panel.
- Quién aprueba una excepción a la fecha de una tarea cuando quien pide ya es el
  aprobador del responsable.
- Si la autoridad del espacio debe enterarse de cada tarea nueva o sólo de lo relevante
  (hoy, sólo lo relevante: mecánica §7; alta de equipo, bloque 2, pregunta 9).
