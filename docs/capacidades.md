# Qué está construido y qué no

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

No se rehace.

| Capacidad | Evidencia |
|---|---|
| Aislamiento entre clientes | Migraciones `0003`–`0005`; regla 1 de [`frontera.md`](architecture/frontera.md) cumplida |
| Estado como proyección de eventos | `bloquear_estado_directo()`; `task.estado` no es editable |
| Reglas de cierre aplicadas en la base | `motivo_no_cierra_tarea()`, `motivo_no_cierra_objetivo()` |
| Alta de tarea propiedad del servidor | `ingreso_tareas.py`: lineage, opciones atómicas, vista previa |
| Router de intención tipado | `llm.py`: un validador cerrado para cuatro proveedores |
| Contrato único de salida | `salida.py`: normalización, medición UTF-16, división |
| Escalera de recordatorios | `escalera.py`: cinco pasos en días hábiles, respeta ausencias |
| Ciclo de vida de un bloqueo | `resolver_bloqueo` cierra y devuelve la tarea al estado previo a `bloqueada`; un bloqueo abierto hace más de `bloqueos.escala_solo_a_los_dias` días hábiles escala solo por la ruta transversal del pack |
| Despacho idempotente | `dedupe_key`, reintento con incidente, respeta jornada |
| Puerto de lectura | `lectura.py`: seis consultas agregadas, el espacio sale de la sesión |
| Tablero de cliente | Credencial por enlace con vencimiento + pantalla |
| Importador de paquetes | Genérico, con validaciones cruzadas y hash versionado |
| Banco conversacional con modelo real | `tests/banco/`: escenarios ficticios en YAML corridos N veces por `gateway.procesar_update` con el proveedor real; comprueba herramientas, acciones afirmadas sin herramienta, personas fuera del equipo, efectos en PostgreSQL y contenido de la respuesta. Fuera de la suite por defecto (`-m modelo_real`); las fallas se guardan para replay |
| Vista previa y confirmación de todo cambio | Las 8 herramientas que escriben (`herramientas.py`, `Herramienta.preparar`) validan autoridad y reglas, muestran estado vigente y cambio propuesto, y esperan Confirmar, Modificar o Cancelar (`pending_action`, migraciones `0009` y `0010`); al confirmar se recalcula una huella del estado y, si cambió, no se aplica. Modificar acepta la corrección durante 30 minutos. El banco toca Confirmar y comprueba que antes no hubo efectos ([`ADR 0005`](decisions/0005-interpretacion-y-confirmacion.md)) |
| Resolución de referencias y aclaración con botones | `route_intent` separa las referencias; Jev (`jev.py`, TypeSafe vía OpenRouter) decide a qué tarea activa del espacio se refiere cada una, con pregunta de verificación, bajo el cursor con RLS (`gateway._turno`). Clara: el modelo recibe la tarea. Dudosa: botones con cada candidata (las propias primero), "Es una tarea nueva" cuando corresponde y "Ninguna, lo escribo"; elegir retoma el mensaje y termina en la vista previa. Sin clave o con Jev caído, pregunta y registra un incidente. Toda respuesta sobre una tarea resuelta nombra su título ([`ADR 0006`](decisions/0006-jev-para-resolver-referencias-e-intencion.md)) |
| Leda orienta con opciones | `ofrecer_opciones` (`herramientas.py`, `MAX_OPCIONES_MODELO = 4`): el modelo pide una elección y el servidor arma botones validados contra PostgreSQL bajo RLS, más "Quiero consultar otra cosa"; tocar una tarea la deja resuelta sin Jev. Menú de tarea (`menu_tarea.calcular_menu`): acciones según estado y relación (responsable, aprobador, otra persona), con vista previa para los cambios. Listas de tareas: el servidor agrega un botón por tarea a toda respuesta que liste tareas (`consultar_tareas`), páginas de 4 con "Ver más" (`gateway._mostrar_mas_tareas`, `ETIQUETA_VER_MAS`), sin depender de que el modelo llame a una herramienta. Cierre genérico: si el turno pregunta en texto abierto sin ningún juego de botones propio, el servidor agrega "Es una tarea nueva" / "Es sobre una tarea existente" / "Quiero consultar otra cosa" (`deteccion_pregunta.py`, `agente._encolar_opciones_genericas`) ([`ADR 0007`](decisions/0007-leda-orienta-no-charla.md), diseño §4.6). Medido con `tests/banco/` y pendiente de una segunda sesión real por Telegram (`odd/tasks/leda-orienta.md`) |
| Autoridad sobre la propia tarea | Cambiar estado y declarar un bloqueo: sólo el responsable; adjuntar evidencia: responsable o su aprobador. Se niega antes de la vista previa (`herramientas.py`, `_preparar_*`). `cancelada` no distingue autoridad superior de responsable: `PENDIENTE` de decisión explícita |
| Fallas con aviso y trazabilidad | Toda falla no manejada al procesar un mensaje o un toque se deshace, registra un incidente que apunta al mensaje o al toque que la causó (`inbound_message`/`pending_action`), con la etapa, la persona, el chat y el error técnico (migración `0011`), y avisa a la persona con un texto neutro (`gateway.procesar_update`, `local.py`); `notificado_en` sólo se completa si el aviso se encoló y la transacción se confirmó de verdad, nunca por adelantado. `python -m leda incidentes` lo muestra. Un rechazo de `preparar` (una preparación que encuentra el mismo impedimento que el handler) se audita como `herramienta_rechazada:<nombre>`, distinto de una ejecución real (`herramienta:<nombre>`), tanto al llamar la herramienta el modelo como al confirmar por botón. Todo incidente, además, avisa a cada administrador de plataforma vinculado al bot de administración (`incidentes.registrar_incidente`, migración `0017`, Constitución §10): el texto incluye qué lo disparó -- el mensaje de la persona o la acción tocada, acotado a 1000 caracteres -- porque §2 ya le da al administrador acceso a esas conversaciones; nunca `referencia_cruda`, que puede traer algo parecido a un secreto. Cada aviso deja además un `audit_log` de ese acceso (§12). `notificado_admin_en` sigue el mismo criterio que `notificado_en`: nunca se completa si nadie era alcanzable |
| Dependencias entre tareas | `crear_dependencia`/`quitar_dependencia` (`herramientas.py`), autoridad del responsable de cualquiera de las dos o su referente; freno de `en_curso` en la base (`motivo_no_arranca_tarea`, migración `0008`); aviso en cadena por atraso o por fecha corrida (`escalera.evaluar_dependencias_en_riesgo`) y aviso de la informativa al cambiar de estado |
| Pregunta pendiente como contexto y una sola rama abierta | Regla 1 del [`ADR 0013`](decisions/0013-reglas-generales-de-la-conversacion.md) y su enmienda. Con una pregunta abierta (dato del menú, Modificar, "Ninguna, lo escribo", campo, elección o confirmación del alta, aclaración con botones, vista previa de un cambio propio), el ruteo tipado devuelve un comando de una lista cerrada y `gateway._atender_pregunta_pendiente` lo maneja de forma determinista (adaptadores en `_pregunta_de`; definición única de rama en `pendientes.ver_rama_abierta`). Otro tema no se atiende: "¿Seguimos con eso?" [Seguir] / [Dejarlo y ver lo otro], y Dejar cierra lo pendiente y atiende el mensaje guardado en la misma respuesta; la guarda `agente.NoProponer` y el bloque "lo que la persona acaba de dejar de lado" impiden volver a proponerlo. Un turno abre como mucho una pregunta. Lo que inicia Leda se retiene mientras la persona está activa en su rama (30 minutos, `despachador.VENTANA_DE_ACTIVIDAD`). Banco: familias `b-0019` a `b-0024` |
| Una respuesta visible por mensaje y por toque | Regla 2 del ADR 0013: cada fila encolada queda atada a su mensaje o toque (migración `0021`, `message_outbox.entrante_id`/`respuesta_grupo`) y `respuesta_unica.controlar` garantiza exactamente una respuesta (sin respuesta: aviso neutro e incidente; varias: queda una e incidente). Fotos, archivos, audios y stickers reciben respuesta (el epígrafe se procesa como texto). Comprobación en todo escenario del banco (`comprobar_una_respuesta_por_entrada`), familia `b-0026` |
| Estado real y sólo opciones posibles | Regla 3 del ADR 0013: un turno que intentó un cambio sin que se ejecutara nada reescribe su respuesta una vez con la corrección del servidor (derivada de los resultados de las herramientas, no de frases); quien pide un alta que confirma otra persona sabe a quién se le mandó; la evidencia sobre una tarea sin entregar dice su estado y ofrece la entrega; el motivo de "Pedir cambios" se ve en el menú y el detalle; el preámbulo no ofrece lo que el sistema no puede hacer. Familia `b-0027` |
| Toques con señal inmediata e idempotentes | Regla 4 del ADR 0013: cada toque se acusa antes de procesarse y corre bajo el indicador de ADR 0011; el mismo `callback_data` de la misma persona en el mismo chat dentro de 10 segundos se absorbe (migración `0022`, `inbound_message.boton_callback`). Familia `b-0028` |
| Modificar en el borrador del alta | Precisión del ADR 0005: la vista previa del borrador (cuando confirma quien lo pidió) tiene Confirmar, Modificar y Cancelar; Modificar abre un selector por dato; un dato de texto se muestra en un bloque copiable con botón de copiar de Telegram (migración `0020`, `message_outbox.bloque_copiable`) y reemplaza sólo ese dato; [Volver al resumen]; sólo Confirmar convierte. Familia `b-0025`. `PENDIENTE` (T9-R1c-4): cuando confirma otra persona, quien pide todavía no revisa su resumen antes de enviarlo |

## Diseñado y sin construir

Cada uno tiene diseño escrito y cero código.

| Área | Lo manda | Estado |
|---|---|---|
| **Entrevista de alta de espacios** | [`nucleo/alta-de-equipo.md`](../nucleo/alta-de-equipo.md), 195 líneas | Sin una sola línea. Sólo existe el importador, que consume un paquete ya escrito. Sin esto, cada cliente nuevo exige que alguien lo escriba a mano |
| **Panel de plataforma** | [`ADR 0004`](decisions/0004-dos-superficies-separadas.md) | Decidido: contraseña + TOTP. Sin construir |
| **Integración de calendario** | Especificación §17.3, constitución §7 | Consultar disponibilidad, proponer, crear, modificar, asistentes. `calendario.py` es el calendario **laboral**, no externo |
| **Correo** | Especificación §18 | Sólo existe el nombre del permiso |
| **Almacenamiento documental** | Especificación §11 | `evidence.drive_file_id` sin uso |
| **Reuniones e informes** | Especificación §17.2 y §23 | Anunciar, pedir temas, consolidar, agenda, minutas. `corework.yaml` declara `reunion_periodica` y el importador no la consume |
| **Conversación de bloqueos** | Mecánica §8, pasos 2 a 7 | Abrir y cerrar un bloqueo ya funciona. Pedir la información mínima, proponer soluciones, preguntar por ayuda y proponer reasignaciones siguen sin construir. Su precondición —dependencias entre tareas— ya está resuelta; es la unidad siguiente en `docs/ROADMAP.md` |
| **Umbral de re-aprobación** | Mecánica §7 | El importador lo guarda en la base y ningún código lo lee |
| **Privacidad configurable** | Especificación §19 | Sin código **ni** esquema. No existe matriz de visibilidad |
| **Aprendizaje** | Mecánica §14 | Tabla `learning` vacía de uso |
| **Bot de administración** | Constitución §2 | Cascarón para lo que la administración escribe: identifica, audita y devuelve `ok`. Ya manda algo de vuelta -- el aviso de cada incidente ("Fallas con aviso y trazabilidad", arriba) -- pero eso es todo: sin comandos, sin consultar nada desde el chat |
| **Atribución de mensajes** | Constitución §7 | Preguntar en nombre de quién va un mensaje. Sólo hay un comentario |

## Trampas conocidas

Verificadas. Cada una engaña a quien la lea.

**Un comentario que miente.** `despachador.py:390` afirma que el tope de
contacto es por persona y no por espacio. El SQL hace el join correcto por
`app_user_id`, pero corre bajo `espacio()` y la RLS confina las tablas al
espacio actual: **el join no puede cruzar**. Quien esté en tres equipos recibe
el triple, y el comentario garantiza que nadie lo revise. Lo exige la mecánica
§10.

**El router de intención no ve las tareas que ya existen.** `route_intent`
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

**`cli.py` está casi sin probar.** `tests/test_cli.py` cubre sólo el cableado
del interruptor `--sin-cadencias` sobre `escuchar` y `servir` (4 pruebas). El
resto de sus trece comandos operativos —`esquema`, `importar`, `despachar`,
`estado`, `incidentes`...— sigue sin ninguna: lo que se usa para operar
Leda de verdad.

**El puerto de lectura no lista tareas.** Sus seis consultas son agregadas, y
las únicas que nombran tareas son vencidas, bloqueadas y esperando aprobación.
Una tarea asignada sin fecha no aparece en ninguna parte del tablero.

## Capacidades construidas que ningún documento describe

Conocimiento que sólo vive en el código: la detección de ambigüedad de nombres
(`contexto.py`), las validaciones cruzadas del importador —cadencia en día no
laboral, volumen de contacto contra el tope, exigencia de suplente— y el
rechazo del token de bot dentro del paquete, porque el paquete se versiona en
git.

## Esquema sin implementación

El inventario **no está acá a propósito**: vive en `tests/test_capacidades.py`,
ejecutable. Dos listas de lo mismo divergen; una prueba no puede pudrirse.

Esa prueba funciona en los dos sentidos. Si alguien implementa una de esas
capacidades, falla y pide que se saque de la lista. Si alguien agrega esquema
nuevo que nadie usa, falla y obliga a decidir si es deuda aceptada o un olvido.

## Vigencia

Levantado el 2026-09-22 auditando `nucleo/`, la especificación funcional y el
código completo. Todo lo de arriba es una foto y envejece; la única parte que
se mantiene sola es la prueba.
