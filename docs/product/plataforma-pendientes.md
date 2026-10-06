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
| Cadencias: qué pide Leda, qué días y a qué hora (estado, resumen grupal, cierre semanal, informe), y la reunión periódica a preparar (`cadencia`, `reunion_periodica`) | Pack | Pedido del usuario (2026-10-01). Una cadencia fuera del horario declarado advierte al configurarla (alta de equipo, "Advierten, pero no impiden") |
| Cuántos días hábiles antes del vencimiento sale el aviso previo de una tarea (un solo aviso; no pide respuesta) | Fijo en el código: un día hábil (`escalera.py`, el paso `-1` de la escalera). En el Motor pasa al pack y después a la plataforma | Decisión del usuario (2026-10-04; ADR 0018, decisión 9b, que enmienda el ADR 0017, decisión 3b): CoreWork, tres días hábiles; mínimo, un día hábil (mecánica §9 permite alargar los intervalos, nunca acortarlos por debajo de un día hábil). Una tarea creada con menos días por delante comprime la escalera |
| A qué hora salen los mensajes que Leda manda por su cuenta (aviso previo, pedidos de estado, repreguntas, escalamientos, avisos guardados) | Fijo en la prueba chica: 10:00 (`HORA_DE_SALIDA`, `prueba_chica/tiempo.py`), dentro del horario del espacio | Una sola hora para todo lo que Leda inicia, para que lo que promete ("mañana a las 10 te vuelvo a preguntar") sea la hora real (2026-10-06). En el producto, un valor de cada espacio |
| Límites de contacto (`limites_de_contacto`) | Pack → `workspace_setting['limites_de_contacto']` | Los avisos de coordinación quedan fuera del tope (mecánica §10) |
| Tiempos de respuesta, urgencia, escalamiento, bloqueos (`tiempos_de_respuesta`, `urgencia`, `escalamiento`, `bloqueos`) | Pack (`bloqueos` → `workspace_setting`) | |
| Tono y conversación (`persona`, `conversacion`): cómo trata Leda a las personas del cliente (`registro`: vos o usted), si usa emojis, formalidad y largo de las respuestas | Pack → `persona_config`; CoreWork: `registro: vos`, `emojis: true` (cambiado el 2026-10-02) | Decisión del usuario (2026-10-02): se configura desde la plataforma. Desde C0-13 (rama de flujo) el código toma el tono del pack en el alta y en la redacción; nunca va escrito en el código |
| Bot y grupo de Telegram (`telegram`) | Pack + secreto en `.env` | El grupo de gestión de CoreWork no existe ("chat not found", STATUS) |
| Objetivos y sus fechas (`objetivo_inicial`, frentes) | Pack | Hoy ningún objetivo tiene fecha: `horizonte_meses: 12` no se convierte al importar |
| Margen máximo de la fecha de una tarea (`horizonte_tarea`, 2 meses, tope 120) | Pack → `workspace_setting` (rama `feat/flujo-de-un-mensaje`) | Regla de fondo decidida: la fecha de una tarea no pasa la de su objetivo; el margen es la red de seguridad |
| Modo del alta (`alta`: `guiada` o `conversada`) | `workspace_setting` por SQL (rama `feat/flujo-de-un-mensaje`) | Experimento del ADR 0014; se retira cuando el alta conversada se adopte |
| Cómo se ve Leda mientras responde: el stream (encendido o apagado, y su modo: real, que muestra el texto mientras el modelo escribe, o progresivo después de verificar), el indicador "escribiendo…" animado (umbral antes de mostrarlo, cada cuánto se renueva) y el borrador nativo de Telegram | `stream` en `workspace_setting` por SQL (rama `feat/flujo-de-un-mensaje`): `true`, `{"activo": true}` o `false`; ausente, apagado; inválido, apagado con incidente `interruptor_stream`; el indicador, con valores fijos en `despachador.mantener_chat_activo` (aparece a los 1,5 s, se renueva cada 3 s) | Pedido del usuario (2026-10-01). Experimento: sólo alta conversada y chat privado; el modo real muestra texto todavía sin verificar. Pendiente comparar los dos modos de stream en real, con el trabajo de latencia (ADR 0011) |
| Variante de redacción (`redaccion`: A o B) | `workspace_setting`, sembrado por el importador | Experimento del ADR 0014 |
| Retención y visibilidad de las conversaciones | Fijado para el piloto por el ADR 0002 | Pasa a ser del cliente; requiere un ADR nuevo |
| Revisión periódica del pack (cada N meses) | No existe | `nucleo/alta-de-equipo.md`, "Revisión periódica" |

## Decisiones abiertas que la plataforma va a necesitar

- Cómo se autentica quien opera Leda.
- Si el tablero de cada cliente muestra sus propios incidentes o sólo el panel.
- Quién aprueba una excepción a la fecha de una tarea cuando quien pide ya es el
  aprobador del responsable.
- Si la autoridad del espacio debe enterarse de cada tarea nueva o sólo de lo relevante
  (hoy, sólo lo relevante: mecánica §7; alta de equipo, bloque 2, pregunta 9).
