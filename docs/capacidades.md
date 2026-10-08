# Qué está construido y qué no

> **Nota del 2026-10-04, actualizada después del paso M1.** Las tablas de este documento
> describen el código de `main`. Su conversación (el alta por chat y los flujos A y B) quedó
> congelada: no se corrige ni se extiende. Qué queda por chat y cómo se cargan las tareas lo fija
> el [ADR 0017](decisions/0017-por-chat-los-hechos-por-la-web-la-estructura.md) (aceptado); el
> motor de conversación del [ADR 0018](decisions/0018-motor-de-conversacion.md) está diseñado y
> **sin construir** ("Diseñado y sin construir", abajo).
>
> **Nota del 2026-10-06 (E3-3 y E3-4).** El código de los flujos A y B (`gateway`, `agente`,
> `contexto`, `ingreso_tareas`, `respuesta_unica`, `deteccion_pregunta`, `jev`, `local`) y las
> tablas del alta guiada (migración `0032`) están borrados. Las filas marcadas "Borrado" quedan
> como historia de lo que hubo; hasta la entrada del motor (E3-7), Leda no recibe mensajes.

Para entender en cinco minutos dónde está parado el proyecto, sin volver a
auditarlo. El detalle vive en los documentos que se citan; acá está el mapa.

## El hallazgo de fondo

El esquema y los documentos describen un producto cerca del doble del código,
y la brecha no es al azar: está sistemáticamente de un lado. Lo construido es
**el registro** —capturar trabajo, aislarlo, entregar mensajes— y ahora
también las dependencias entre tareas. Lo ausente sigue siendo el resto de
**la coordinación** —subtareas, prioridad, reuniones, informes, calendario,
correo, umbral de re-aprobación—, que es justamente la misión del §2: reducir
"dependencias invisibles" y "reuniones dedicadas únicamente a recopilar
estado".

Leda hoy es un registro de tareas bien construido con interfaz de Telegram.

## Construido y sólido

No se rehace, con una salvedad del 2026-10-04. Las filas que describen la conversación (el alta de
tarea por chat, el ruteo de intención, la aclaración con botones, "Leda orienta con opciones", la
pregunta pendiente, la respuesta única, el estado real, los toques y Modificar) corresponden a los
flujos A y B, cuyo código se borró en la Etapa 3 del Motor (E3-3 y E3-4). Las demás filas son la
capa de garantías y de dominio, que sí se conserva. El motor de conversación reutiliza la vista
previa con huella (ADR 0018, decisión 2), dejó a Jev fuera (nota de la decisión 7) y toma las
reglas del ADR 0013 como comportamiento, no como código. La lista de piezas que se reutilizan está en el documento de la unidad, "Lo sólido
que se reutiliza".

| Capacidad | Evidencia |
|---|---|
| Aislamiento entre clientes | Migraciones `0003`–`0005`; regla 1 de [`frontera.md`](architecture/frontera.md) cumplida |
| Estado como proyección de eventos | `bloquear_estado_directo()`; `task.estado` no es editable |
| Reglas de cierre aplicadas en la base | `motivo_no_cierra_tarea()`, `motivo_no_cierra_objetivo()` |
| Alta de tarea propiedad del servidor | **Borrado (E3-3 y E3-4).** `ingreso_tareas.py`: lineage, opciones atómicas, vista previa |
| Router de intención tipado | **Borrado (E3-3 y E3-4).** `llm.py`: un validador cerrado para cuatro proveedores |
| Contrato único de salida | `salida.py`: normalización, medición UTF-16, división |
| Escalera de recordatorios | `escalera.py`: cinco pasos en días hábiles, respeta ausencias |
| Ciclo de vida de un bloqueo | `resolver_bloqueo` cierra y devuelve la tarea al estado previo a `bloqueada`; un bloqueo abierto hace más de `bloqueos.escala_solo_a_los_dias` días hábiles escala solo por la ruta transversal del pack |
| Despacho idempotente | `dedupe_key`, reintento con incidente, respeta jornada |
| Puerto de lectura | `lectura.py`: seis consultas agregadas, el espacio sale de la sesión |
| Tablero de cliente | Credencial por enlace con vencimiento + pantalla de sólo lectura (`GET /tablero/{token}`); no lista las tareas con su estado |
| Importador de paquetes | Genérico, con validaciones cruzadas y hash versionado |
| Banco conversacional con modelo real | **Borrado (E3-3 y E3-4).** `tests/banco/`: escenarios ficticios en YAML corridos N veces por `gateway.procesar_update` con el proveedor real; comprueba herramientas, acciones afirmadas sin herramienta, personas fuera del equipo, efectos en PostgreSQL y contenido de la respuesta. Fuera de la suite por defecto (`-m modelo_real`); las fallas se guardan para replay |
| Vista previa y confirmación de todo cambio | Las 8 herramientas que escriben (`herramientas.py`, `Herramienta.preparar`) validan autoridad y reglas, muestran estado vigente y cambio propuesto, y esperan Confirmar, Modificar o Cancelar (`pending_action`, migraciones `0009` y `0010`); al confirmar se recalcula una huella del estado y, si cambió, no se aplica. Modificar acepta la corrección durante 30 minutos. Modificar y el banco se borraron con los flujos A y B; Confirmar y Cancelar, la huella y `resolver_pendiente` quedan ([`ADR 0005`](decisions/0005-interpretacion-y-confirmacion.md)) |
| Resolución de referencias y aclaración con botones | **Borrado (E3-3 y E3-4).** `route_intent` separa las referencias; Jev (`jev.py`, TypeSafe vía OpenRouter) decide a qué tarea activa del espacio se refiere cada una, con pregunta de verificación, bajo el cursor con RLS (`gateway._turno`). Clara: el modelo recibe la tarea. Dudosa: botones con cada candidata (las propias primero), "Es una tarea nueva" cuando corresponde y "Ninguna, lo escribo"; elegir retoma el mensaje y termina en la vista previa. Sin clave o con Jev caído, pregunta y registra un incidente. Toda respuesta sobre una tarea resuelta nombra su título ([`ADR 0006`](decisions/0006-jev-para-resolver-referencias-e-intencion.md)) |
| Leda orienta con opciones | **Borrado (E3-3 y E3-4).** El menú de tarea, las listas con "Ver más" y el cierre genérico; `ofrecer_opciones` queda en `herramientas.py`. Era: `ofrecer_opciones` (`herramientas.py`, `MAX_OPCIONES_MODELO = 4`): el modelo pide una elección y el servidor arma botones validados contra PostgreSQL bajo RLS, más "Quiero consultar otra cosa"; tocar una tarea la deja resuelta sin Jev. Menú de tarea (`menu_tarea.calcular_menu`): acciones según estado y relación (responsable, aprobador, otra persona), con vista previa para los cambios. Listas de tareas: el servidor agrega un botón por tarea a toda respuesta que liste tareas (`consultar_tareas`), páginas de 4 con "Ver más" (`gateway._mostrar_mas_tareas`, `ETIQUETA_VER_MAS`), sin depender de que el modelo llame a una herramienta. Cierre genérico: si el turno pregunta en texto abierto sin ningún juego de botones propio, el servidor agrega "Es una tarea nueva" / "Es sobre una tarea existente" / "Quiero consultar otra cosa" (`deteccion_pregunta.py`, `agente._encolar_opciones_genericas`) ([`ADR 0007`](decisions/0007-leda-orienta-no-charla.md), diseño §4.6). Medido con `tests/banco/` y pendiente de una segunda sesión real por Telegram (`odd/tasks/leda-orienta.md`) |
| Autoridad sobre la propia tarea | Cambiar estado y declarar un bloqueo: sólo el responsable; adjuntar evidencia: responsable o su aprobador. Se niega antes de la vista previa (`herramientas.py`, `_preparar_*`). `cancelada` no distingue autoridad superior de responsable: `PENDIENTE` de decisión explícita |
| Fallas con aviso y trazabilidad | Toda falla no manejada al procesar un mensaje o un toque se deshace, registra un incidente que apunta al mensaje o al toque que la causó (`inbound_message`/`pending_action`), con la etapa, la persona, el chat y el error técnico (migración `0011`), y avisa a la persona con un texto neutro (lo hacían `gateway.procesar_update` y `local.py`, borrados; hoy el motor de conversación (`leda.motor.recibir`) y el barrido de huérfanos, `huerfanos.py`); `notificado_en` sólo se completa si el aviso se encoló y la transacción se confirmó de verdad, nunca por adelantado. `python -m leda incidentes` lo muestra. Un rechazo de `preparar` (una preparación que encuentra el mismo impedimento que el handler) se audita como `herramienta_rechazada:<nombre>`, distinto de una ejecución real (`herramienta:<nombre>`), tanto al llamar la herramienta el modelo como al confirmar por botón. Todo incidente, además, avisa a cada administrador de plataforma vinculado al bot de administración (`incidentes.registrar_incidente`, migración `0017`, Constitución §10): el texto incluye qué lo disparó -- el mensaje de la persona o la acción tocada, acotado a 1000 caracteres -- porque §2 ya le da al administrador acceso a esas conversaciones; nunca `referencia_cruda`, que puede traer algo parecido a un secreto. Cada aviso deja además un `audit_log` de ese acceso (§12). `notificado_admin_en` sigue el mismo criterio que `notificado_en`: nunca se completa si nadie era alcanzable |
| Dependencias entre tareas | `crear_dependencia`/`quitar_dependencia` (`herramientas.py`), autoridad del responsable de cualquiera de las dos o su referente; freno de `en_curso` en la base (`motivo_no_arranca_tarea`, migración `0008`); aviso en cadena por atraso o por fecha corrida (`escalera.evaluar_dependencias_en_riesgo`) y aviso de la informativa al cambiar de estado |
| Pregunta pendiente como contexto y una sola rama abierta | **Borrado (E3-3 y E3-4).** También la retención de lo que inicia Leda en el despachador. Era: regla 1 del [`ADR 0013`](decisions/0013-reglas-generales-de-la-conversacion.md) y su enmienda. Con una pregunta abierta (dato del menú, Modificar, "Ninguna, lo escribo", campo, elección o confirmación del alta, aclaración con botones, vista previa de un cambio propio), el ruteo tipado devuelve un comando de una lista cerrada y `gateway._atender_pregunta_pendiente` lo maneja de forma determinista (adaptadores en `_pregunta_de`; definición única de rama en `pendientes.ver_rama_abierta`). Otro tema no se atiende: "¿Seguimos con eso?" [Seguir] / [Dejarlo y ver lo otro], y Dejar cierra lo pendiente y atiende el mensaje guardado en la misma respuesta; la guarda `agente.NoProponer` y el bloque "lo que la persona acaba de dejar de lado" impiden volver a proponerlo. Un turno abre como mucho una pregunta. Lo que inicia Leda se retiene mientras la persona está activa en su rama (30 minutos, `despachador.VENTANA_DE_ACTIVIDAD`). Banco: familias `b-0019` a `b-0024` |
| Una respuesta visible por mensaje y por toque | **Borrado (E3-3 y E3-4).** Queda la columna `message_outbox.entrante_id`. Era: regla 2 del ADR 0013: cada fila encolada queda atada a su mensaje o toque (migración `0021`, `message_outbox.entrante_id`/`respuesta_grupo`) y `respuesta_unica.controlar` garantiza exactamente una respuesta (sin respuesta: aviso neutro e incidente; varias: queda una e incidente). Fotos, archivos, audios y stickers reciben respuesta (el epígrafe se procesa como texto). Comprobación en todo escenario del banco (`comprobar_una_respuesta_por_entrada`), familia `b-0026` |
| Estado real y sólo opciones posibles | **Borrado (E3-3 y E3-4).** Era: regla 3 del ADR 0013: un turno que intentó un cambio sin que se ejecutara nada reescribe su respuesta una vez con la corrección del servidor (derivada de los resultados de las herramientas, no de frases); quien pide un alta que confirma otra persona sabe a quién se le mandó; la evidencia sobre una tarea sin entregar dice su estado y ofrece la entrega; el motivo de "Pedir cambios" se ve en el menú y el detalle; el preámbulo no ofrece lo que el sistema no puede hacer. Familia `b-0027` |
| Toques con señal inmediata e idempotentes | **Borrado (E3-3 y E3-4).** Era: regla 4 del ADR 0013: cada toque se acusa antes de procesarse y corre bajo el indicador de ADR 0011; el mismo `callback_data` de la misma persona en el mismo chat dentro de 10 segundos se absorbe (migración `0022`, `inbound_message.boton_callback`). Familia `b-0028` |
| Modificar en el borrador del alta | **Borrado (E3-3 y E3-4).** Era: precisión del ADR 0005: la vista previa del borrador (cuando confirma quien lo pidió) tiene Confirmar, Modificar y Cancelar; Modificar abre un selector por dato; un dato de texto se muestra en un bloque copiable con botón de copiar de Telegram (migración `0020`, `message_outbox.bloque_copiable`) y reemplaza sólo ese dato; [Volver al resumen]; sólo Confirmar convierte. Familia `b-0025`. `PENDIENTE` (T9-R1c-4): cuando confirma otra persona, quien pide todavía no revisa su resumen antes de enviarlo |

## Diseñado y sin construir

Cada uno tiene diseño escrito y cero código, salvo la plataforma web de tareas, que todavía
no tiene su diseño.

| Área | Lo manda | Estado |
|---|---|---|
| **Motor de conversación (flujo D)** | [`ADR 0018`](decisions/0018-motor-de-conversacion.md), aceptado el 2026-10-06, después de la prueba chica (M2) | Sin código. La IA elige jugadas de una lista cerrada y el código las comprueba y ejecuta; estado por persona y registro de turnos; circuitos declarados con fichas y ocho situaciones generales. La prueba chica de la Etapa 2 vive fuera de `src/leda`; el motor definitivo, en la Etapa 3 |
| **Lo que le falta al seguimiento** | [`ADR 0017`](decisions/0017-por-chat-los-hechos-por-la-web-la-estructura.md), decisiones 4 y 6 | No hay enlace entre una respuesta y su recordatorio; `pending_reply` existe y nada la escribe; los textos de recordatorios y cadencias están fijos en `escalera.py` y `reloj.py`; no existe la operación de pedir más tiempo. Relevamiento del 2026-10-04 ([`STATUS.md`](STATUS.md), "Estado comprobado") |
| **Plataforma web de tareas** | [`ADR 0017`](decisions/0017-por-chat-los-hechos-por-la-web-la-estructura.md), decisión 5 | Sin diseño propio todavía: lleva su ADR antes del código. Para cargar tareas sólo existe `sembrar`, un cargador de datos ficticios que no cumple las condiciones de la carga (decisión 2) |
| **Entrevista de alta de espacios** | [`nucleo/alta-de-equipo.md`](../nucleo/alta-de-equipo.md), 195 líneas | Sin una sola línea. Sólo existe el importador, que consume un paquete ya escrito. Sin esto, cada cliente nuevo exige que alguien lo escriba a mano. No aplica en esta etapa (ADR 0017, decisión 7) |
| **Panel de plataforma** | [`ADR 0004`](decisions/0004-dos-superficies-separadas.md) | Decidido: contraseña + TOTP. Sin construir |
| **Integración de calendario** | Especificación §17.3, constitución §7 | Consultar disponibilidad, proponer, crear, modificar, asistentes. `calendario.py` es el calendario **laboral**, no externo |
| **Correo** | Especificación §18 | Sólo existe el nombre del permiso |
| **Almacenamiento documental** | Especificación §11 | `evidence.drive_file_id` sin uso |
| **Reuniones e informes** | Especificación §17.2 y §23 | Anunciar, pedir temas, consolidar, agenda, minutas. `corework.yaml` declara `reunion_periodica` y el importador no la consume |
| **Conversación de bloqueos** | Mecánica §8, pasos 2 a 7 | Abrir y cerrar un bloqueo ya funciona. Pedir la información mínima, proponer soluciones, preguntar por ayuda y proponer reasignaciones siguen sin construir. Su precondición —dependencias entre tareas— ya está resuelta. El ADR 0017 (decisión 3a) la pone en el seguimiento de esta etapa, ampliada: perseguir el bloqueo de persona en persona hasta quien puede destrabarlo. La prueba chica cubre sólo el primer paso, anotarlo (ADR 0018, decisión 5a) |
| **Umbral de re-aprobación** | Mecánica §7 | El importador lo guarda en la base y ningún código lo lee. En esta etapa se resuelve en la plataforma (ADR 0017, decisión 7) |
| **Privacidad configurable** | Especificación §19 | Sin código **ni** esquema. No existe matriz de visibilidad |
| **Aprendizaje** | Mecánica §14 | Tabla `learning` vacía de uso |
| **Bot de administración** | Constitución §2 | Cascarón para lo que la administración escribe: identifica, audita y devuelve `ok`. Ya manda algo de vuelta -- el aviso de cada incidente ("Fallas con aviso y trazabilidad", arriba) -- pero eso es todo: sin comandos, sin consultar nada desde el chat |
| **Atribución de mensajes** | Constitución §7 | Preguntar en nombre de quién va un mensaje. Sólo hay un comentario |

## Trampas conocidas

Verificadas. Cada una engaña a quien la lea.

**Un comentario que miente.** `despachador._ya_recibio` afirma que el tope de
contacto es por persona y no por espacio. El SQL hace el join correcto por
`app_user_id`, pero corre bajo `espacio()` y la RLS confina las tablas al
espacio actual: **el join no puede cruzar**. Quien esté en tres equipos recibe
el triple, y el comentario garantiza que nadie lo revise. Lo exige la mecánica
§10.

**El router de intención no ve las tareas que ya existen.** Historia: el router se borró con los
flujos A y B (E3-3). `route_intent`
recibe sólo el texto del mensaje (`llm.ROUTER_SYSTEM`), no las tareas del
espacio. "El cableado del tablero no puede arrancar hasta que yo termine de
programar el PLC, dejalo anotado" —dos tareas ya cargadas— se clasificó como
pedido de tarea nueva en 10 de 10 corridas del banco (escenario `b-0005`,
2026-09-23, NaN `deepseek-v4-flash`): abre el alta guiada y la dependencia nunca
se crea. Un replay guionado no sirve de regresión, porque repite la
clasificación grabada; la regresión es el escenario contra el modelo real.
**Corregido el 2026-09-24** (unidad de aclaración con botones): una referencia que Jev
resuelve con claridad a una tarea existente ya no abre el alta de tarea nueva, y en el
caso mixto Leda pregunta con "Es una tarea nueva" entre las opciones. En la última
corrida del banco real, `b-0005` y `b-0005-a` pasan 6 de 6; `b-0005-b` pregunta de más
en 3 de 3.

**`cli.py` está casi sin probar.** `tests/test_cli.py` cubre sólo el arranque de
`servir` (el interruptor `--sin-cadencias` y el chequeo de migraciones, 3 pruebas). El
resto de sus comandos operativos —`esquema`, `importar`, `despachar`,
`estado`, `incidentes`...— sigue sin ninguna: lo que se usa para operar
Leda de verdad.

**El puerto de lectura no lista tareas.** Sus seis consultas son agregadas, y
las únicas que nombran tareas son vencidas, bloqueadas y esperando aprobación.
Una tarea asignada sin fecha no aparece en ninguna parte del tablero.

## Capacidades construidas que ningún documento describe

Conocimiento que sólo vive en el código: las validaciones cruzadas del importador —cadencia en día no
laboral, volumen de contacto contra el tope, exigencia de suplente— y el
rechazo del token de bot dentro del paquete, porque el paquete se versiona en
git.

## Esquema sin implementación

El inventario **no está acá a propósito**: vive en `tests/garantias/test_capacidades.py`,
ejecutable. Dos listas de lo mismo divergen; una prueba no puede pudrirse.

Esa prueba funciona en los dos sentidos. Si alguien implementa una de esas
capacidades, falla y pide que se saque de la lista. Si alguien agrega esquema
nuevo que nadie usa, falla y obliga a decidir si es deuda aceptada o un olvido.

## Lo que agregó el motor después de M3 (2026-10-07 y 08)

Código en `src/leda/motor/`, `src/leda/salida.py` y `src/leda/despachador.py`; evidencia en la bitácora de flujos.

| Capacidad | Dónde |
|---|---|
| Los datos que lee la IA al redactar tienen nombres de todos los días, sin conceptos del sistema | `hechos.para_redactar` |
| A la persona, Leda no nombra por su cuenta a quien aprueba su trabajo (decisión 11 del usuario, 2026-10-08): la redacción recibe ese nombre dentro de `solo_si_pregunta`, en el mismo lugar del dato que lo nombra, y lo dice si la persona pregunta; los hechos de la cocina y el registro de turnos lo guardan igual. Lo que espera una decisión se dice revisión ("pasa a revisión", "para revisar"; decisión 18), también en la página de la tarea ("en revisión") | `hechos.NOMBRAN_A_QUIEN_APRUEBA_SU_TRABAJO`, `hechos.para_redactar`, `tarea_vista.ESTADOS` |
| Formato de los mensajes: un renglón por idea, 📋 ✏️ 🗓️ ⚠️ al principio del renglón, fechas cortas, cierre aparte; medido por el corredor | `instrucciones.py`, `tests/conversaciones/comprobar.py` |
| Negrita por entidades de Telegram, sin `parse_mode` (hoy la instrucción no la pide) | `salida.formatear` |
| "Escribiendo…", borrador "…" y el texto de la respuesta en vivo; el mensaje final sale enseguida | `despachador.py`, `recibir.py` |
| Rastro de cada intento fallido de redactar un aviso (incidente de severidad baja) | `avisos.py` |
| Margen de 10 minutos antes de los avisos a otra persona, para que una corrección retire el equivocado | `margen.py` |
| Una fecha que atrasa sin motivo: Leda lo pregunta y el aviso espera la respuesta o sale al final del día | `fichas.py` |
| Recibir y guardar fotos, documentos, videos y álbumes (sin evidencia todavía), con límites por contenido | `archivos.py`, migración `0033` |
| La política de evidencia se cumple por tipo: cada tipo pedido, una pieza propia del ciclo vigente, no retirada, de una clase que ese tipo acepta (una frase sola no cubre una foto); la evidencia y sus retiros no se editan ni se borran; la cocina entrega con las piezas y el paso a revisión en un solo acto (`entregar_tarea`) y retira una pieza (`retirar_evidencia`) | migración `0034`, `herramientas.py`, `evidencia.tipos` del pack |
| La salida con adjuntos: una fila de la salida lleva hasta diez archivos del dominio, en orden (`message_outbox_adjunto`, sin columnas nuevas en `message_outbox`); el despachador manda el álbum después de su texto (si el texto no sale, el álbum tampoco), reusando el identificador que Telegram le dio a cada foto al recibirla y, si no sirve, subiendo la copia propia | migración `0035`, `salida.py` (`enqueue_outbox(adjuntos=…)`), `despachador.py` (`enviar_album`) |
| La entrega por chat: "terminé" con o sin fotos muestra cada pieza (también lo mandado antes, que entra sólo si queda), qué cubre y qué falta; se confirma con el botón o por escrito, con la guarda (lo último que vio y sin cambios); al confirmar, la tarea pasa a revisión, nunca a terminada; una pieza se saca de la vista previa o, entregada, se retira; un archivo sin entrega abierta lleva la pregunta de para qué tarea es (una sola vez, aunque la jugada que lo tomó no diga la tarea). Un texto cubre siempre lo que sólo un texto puede cubrir. | `entrega.py`, `fichas.py` (`entregar`, `confirmar`, `guardar_para_la_entrega`) |
| La entrega frente al criterio de aceptación (C-3d, D3; decisión 10 del usuario): el criterio se lee por puntos (renglones, oraciones y punto y coma); la IA juzga qué puntos dice lo descrito (`lo_descrito_cubre`) y propone un ejemplo para lo que falta; el código decide qué falta y si se ofrece Confirmar, y verifica que el ejemplo no traiga un número ni un nombre que no estén en el criterio, la tarea o lo que escribió la persona (si no, propone el punto tal cual). Sin cubrir el criterio no se entrega aunque la persona insista; el ejemplo cuenta sólo si la persona lo acepta (`acepta_el_ejemplo`). Cada texto guarda los puntos que describe (`evidence.describe_del_criterio`, migración `0038`) | `entrega.py` (`puntos_del_criterio`, `problema_del_ejemplo`), `fichas.py`, `herramientas.py` (`entregar_tarea`) |
| Entregar una tarea que nunca se arrancó (decisión 14): se recibe igual, con su vista previa; al confirmar, la historia dice que arrancó y se entregó en ese momento (dos eventos de la persona, sin fecha de inicio inventada), nunca terminada; no arranca con una dependencia bloqueante sin terminar | `herramientas.py` (`entregar_tarea`), `entrega.py` |
| Una pieza retirada que deja la entrega incompleta (decisión 15): Leda dice qué falta y pide la pieza correcta, con el mismo ejemplo para el criterio; mientras falta, el aviso a quien aprueba que no salió queda omitido y aprobar no cambia nada (se le dice que la entrega se está completando); con la pieza nueva confirmada, la cocina la suma a la tarea en revisión sin moverla y a quien aprueba le llega un aviso nuevo con todo (T6i). `PENDIENTE`: los recordatorios a quien aprueba no esperan mientras la entrega está incompleta | `entrega.py` (`corregir`, `falta_algo_de_lo_entregado`), `avisos.py`, `aprobacion.py`, `herramientas.py` |
| El aviso de una entrega a quien la aprueba, del motor (porción 3a): guardado como hechos al confirmar, sale terminado el margen para corregir; al salir relee la tarea y la evidencia vigente (sin lo retirado) y, si la tarea ya no espera la aprobación, queda omitido con su motivo; la IA lo redacta desde esos hechos; las fotos van adjuntas (hasta diez, como álbum, después del texto) y los demás archivos sólo se nombran; es de coordinación, fuera del tope diario; una entrega nueva retira el aviso que espera (T6i). Desde la porción 3b ofrece los botones Aprobar y Pedir cambios con su texto (no con el álbum); desde la 4, lleva al final el enlace a la página de la tarea. Las entregas de la cocina que ningún circuito del chat alcanza (`actualizar_estado` a revisión, `adjuntar_evidencia`) siguen con el texto fijo de `_notificar_entrega_al_aprobador` | `avisos.py` (`entrega_para_aprobar`, `guardar_aviso_de_entrega`), `entrega.py` (`confirmar`) |
| La hoja de aprobación por chat (circuito 8, porción 3b): quien aprueba ve las entregas que esperan su decisión; "aprobado" claro va directo, sin vista previa, y la cocina comprueba el cierre en el mismo acto (sin la política de evidencia completa, no se aprueba); "pedir cambios" sin decir qué falta lo pregunta, y con lo que falta la tarea vuelve al estado de antes de entregarla; aprobar y pedir cambios juntos sobre la misma tarea no hacen nada y llevan una sola pregunta con dos botones, y lo mismo una aprobación con un comentario para el responsable, que nunca cierra directo (decisión 22, C-3d, D7b: lo decide la cocina; la IA sólo dice que trae un comentario); la pregunta se hace una sola vez (C-3d, D4, decisión 12): la respuesta elige y lo demás va como comentario al responsable; si no elige (o vuelve a mezclar las dos), Leda no decide ni repite la pregunta y la entrega sigue esperando, con Aprobar y Pedir cambios en la respuesta (`situaciones.sin_elegir`, `TipoDePregunta.sin_elegir_queda`); los botones del aviso son atajos, con la guarda (si la entrega cambió desde el aviso, el botón no vale; uno ya decidido no hace nada y lo dice); sólo quien aprueba ese trabajo decide, nadie su propio trabajo; los avisos de la decisión al responsable los redacta el motor y salen enseguida (la cocina dejó de mandar sus textos fijos en `aprobar_tarea` y `pedir_cambios_tarea`) | `aprobacion.py`, `fichas.py` (`aprobar`, `pedir_cambios`, `dos_lecturas`), `avisos.py` (`tarea_aprobada`, `pedido_de_cambios`), `botones.py` |
| Las entregas para revisar en listas (C-3d, D4, decisiones 17 y 18; conversación 28): los avisos de entrega a una persona que salen juntos van en un solo mensaje, con cada tarea, quién la entregó y cuántas fotos trae, y un botón por tarea ("Ver" y la tarea); uno solo sale como siempre (fotos, enlace, Aprobar y Pedir cambios). Ver una entrega es una jugada (`ver_entrega`), tocada o escrita: la respuesta trae lo entregado, las fotos en un álbum, el enlace a la página de la tarea y Aprobar y Pedir cambios, sin ser un tema abierto. Después de decidir una, la respuesta dice lo que queda por revisar, con un botón por tarea, sin insistir ese día. El tope diario cuenta mensajes; los avisos de coordinación siguen fuera | `avisos.py` (`TipoDeAviso.se_agrupa`, `ofrece_ver`), `aprobacion.py` (`ver_entrega`, `_lo_que_queda`), `preguntas.py` (`VER_LA_ENTREGA`, `ofrecer_en_la_respuesta`), `turno.py`, `botones.py` |
| Si cambia quién aprueba (C-3d, D4, decisión 16; conversación 29): el aviso de una entrega va a quien aprueba al salir (se relee); si el cambio es después de que salió, la escalera le guarda al nuevo el aviso de lo que espera su decisión, una vez; el botón del aviso viejo le dice al anterior que esa tarea ya no la revisa él, sin cambiar nada (`ya_no_le_corresponde`) | `avisos.py` (`TipoDeAviso.va_a`), `escalera.py` (`_a_quien_aprueba_ahora`), `situaciones.py` |
| Una aprobación que todavía no puede cerrar queda anotada; en cada vuelta del ciclo el sistema vuelve a comprobar el cierre y, cuando se resolvió lo que faltaba (una dependencia que terminó o se canceló, un bloqueo cerrado), la cierra sola con esa aprobación (evento del sistema que la nombra, auditado), sin otra aprobación, con aviso al responsable y a quien aprobó | `herramientas.py` (`cerrar_tarea_aprobada`), `aprobacion.cerrar_las_que_ya_pueden`, `ciclo.py`, `avisos.py` (`cerrada_con_la_aprobacion`) |
| Quien aprueba no contesta (porción 3c; conversación 24): una entrega que espera la decisión tiene su escalera, en días hábiles desde que salió el aviso de la entrega (sin otra espera); un recordatorio a quien aprueba el día hábil siguiente y otro al segundo, que avisa que al día siguiente se entera quien está arriba (quien aprueba su trabajo, si hay alguien y no es el responsable); al tercero, a quien está arriba un aviso sólo informativo, una vez, sin botones ni pregunta (no lo convierte en aprobador); después, un recordatorio cordial por día hábil hasta decidir; con nadie arriba, sólo el recordatorio diario. Los recordatorios recuerdan la decisión que ofreció el aviso de la entrega, sin abrir otra pregunta, y desde la D4 de la C-3d llevan un botón por tarea para verla (decisión 17); se releen al salir y se omiten con su motivo si ya decidió (también una aprobación que todavía no cierra), si la entrega ya no espera o hay otra más nueva, o si cambió quién aprueba o quién está arriba; dentro del horario, un paso por día hábil, en pausa mientras quien aprueba está ausente. Una decisión corta los recordatorios y, si quien está arriba ya se había enterado, le llega que se destrabó (de coordinación, enseguida). Al responsable nunca le llega nada de esto. Los recordatorios y el aviso a quien está arriba cuentan para el tope diario (`PENDIENTE` de confirmar con el usuario) | `escalera.py` (`_un_paso_de_una_decision`), `avisos.py` (`recordatorio_de_la_decision`, `aprobacion_trabada`, `aprobacion_destrabada`, `TipoDeAviso.recuerda`), `aprobacion.py` (`_avisar_que_se_destrabo`) |
| La página de una tarea (porción 4; ADR 0019, decisión 7): de sólo lectura, con un enlace personal por persona y por tarea que no vence (sólo su hash en la base, revocable); la ven el responsable, quien aprueba su trabajo y quien ya decidió sobre ella, el referente del área (dato del pack, `areas[].referente`) y la autoridad final, revalidado en cada pedido; muestra la tarea, su historia y su evidencia en palabras de todos los días (las imágenes se ven, lo demás se baja, lo retirado figura como retirado), nunca la conversación; cada vista y cada descarga quedan registradas; sale con `no-store`, `no-referrer`, `noindex`, `nosniff` y una política de contenido que no ejecuta nada | migración `0036`, `pagina_de_tarea.py`, `tarea_vista.py`, `entrada.py` (`GET /tarea/{token}`) |
| El enlace a esa página en los avisos: a quien aprueba, en el de la entrega; al responsable, en los de la decisión. La IA sabe que va, nunca lo ve; la salida guarda sólo la marca (`message_outbox_enlace`) y el despachador lo emite al mandar, sin vista previa; sin la dirección pública configurada (`LEDA_BASE_URL`) no se promete ni se manda. Pedirlo por chat (una jugada nueva) todavía no existe | `avisos.py` (`TipoDeAviso.enlace`), `salida.py`, `despachador.py` |
| No interrumpir una conversación (C-3d, D5; decisión 13 del usuario, conversación 26): lo que Leda manda por su cuenta a una persona, también un aviso de coordinación, espera 30 minutos desde lo último que esa persona escribió o tocó (`no_interrumpir_minutos` del espacio), y cada mensaje vuelve a contar; nunca fuera del horario (si la espera cruza el cierre, sale el día hábil siguiente a la hora de salida); a otra persona no la demora. Con una pregunta de Leda sin contestar, ningún aviso sale junto con ella: la pregunta misma, repetida por la escalera, sale sola; uno de otra tarea que no pide respuesta sale aparte, sin pregunta; uno que pide respuesta (una pregunta o decidir) y uno de la misma tarea esperan a que se cierre. Al salir se relee, y el aviso previo y el recordatorio del vencimiento de una tarea de la que la persona habló después de que se guardaron no salen (`ya_se_hablo_de_la_tarea`). Lo que se le cuenta a otra persona dice cuándo se entera de verdad (si está conversando, al terminar su espera). Avisos de entrega confirmados con minutos de diferencia que esperan juntos salen en una lista | `no_interrumpir.py`, `avisos.py` (`_preparar`, `_un_tema_a_la_vez`, `TipoDeAviso.se_omite_si_ya_se_hablo`), `efectos.py` |
| El lector de turnos y avisos guardados | `leda.motor.leer` |

## Vigencia

Levantado el 2026-09-22 auditando `nucleo/`, la especificación funcional y el
código completo; notas del 2026-10-04 con los ADR 0017 y 0018. Todo lo de arriba es
una foto y envejece; la única parte que se mantiene sola es la prueba.
