# Pendientes para la plataforma

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

## Configuración de cada espacio

Lo que hoy sale del pack (`espacios/<espacio>.yaml`, se cambia editando y reimportando) o
de `workspace_setting` (se cambia por SQL).

| Qué | Hoy | Notas |
|---|---|---|
| Identidad, glosario, vocabulario y niveles (`espacio`, `glosario`, `niveles`) | Pack | Nombres visibles de cada nivel de trabajo (mecánica §1) |
| Integrantes y roles: alta y baja de personas, su área, su rol, a quién aprueban y quién las aprueba, ausencias (`areas`, `roles`, `personas`) | Pack, reimportando | Pedido del usuario (2026-10-01). Quién aprueba a quién (`aprobado_por`) define el botón Confirmar o Enviar a aprobación. Una baja no puede dejar tareas sin responsable ni un área sin aprobador (validaciones de `nucleo/alta-de-equipo.md`) |
| Política de aprobación (`aprobacion`) | Pack | Pendiente: quién aprueba una excepción cuando quien pide ya es el aprobador ("Trabajo que no entra en una tarea") |
| Evidencia por área (`evidencia`) | Pack | Hoy se muestra con claves internas ("explicacion"): falta su nombre legible |
| Horario laboral del equipo, horarios distintos por persona y feriados (`calendario`) | Pack + `python -m leda feriados <espacio>` | Pedido del usuario (2026-10-01): define cuándo salen los avisos. CoreWork, 09:00-17:00. Fuera de horario Leda no escribe (constitución §8): un aviso de las 18 sale a las 9 del día siguiente. Horario por persona: alta de equipo, bloque 2, pregunta 6. Urgencia fuera de horario sólo por regla aprobada (mecánica §11) |
| Cadencias: qué pide Leda, qué días y a qué hora (estado, resumen grupal, cierre semanal, informe), y la reunión periódica a preparar (`cadencia`, `reunion_periodica`) | Pack | Pedido del usuario (2026-10-01). Una cadencia fuera del horario declarado advierte al configurarla (alta de equipo, "Advierten, pero no impiden") |
| Límites de contacto (`limites_de_contacto`) | Pack → `workspace_setting['limites_de_contacto']` | Los avisos de coordinación quedan fuera del tope (mecánica §10) |
| Tiempos de respuesta, urgencia, escalamiento, bloqueos (`tiempos_de_respuesta`, `urgencia`, `escalamiento`, `bloqueos`) | Pack (`bloqueos` → `workspace_setting`) | |
| Tono y conversación (`persona`, `conversacion`) | Pack | |
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
