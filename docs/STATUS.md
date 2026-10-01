# Estado actual

**Alcance:** Prisma es un producto de gestión de proyectos multi-tenant. CoreWork es
su primer cliente, no su definición.

**Última actualización documental:** 2026-09-30.

Historia de sesiones y unidades cerradas:
[`historial/STATUS-hasta-2026-09-30.md`](historial/STATUS-hasta-2026-09-30.md)
(copia literal de este documento antes de su condensación).

## Resumen

Prisma se define como producto ofrecible a varios clientes, con superficie
conversacional, superficie de lectura y eventual aplicación móvil. La capa de datos
funciona (sabe con quién habla, no mezcla tareas de otras personas, los flujos de alta,
entrega y aprobación avanzan de punta a punta), pero la conversación se siente
"robótica" y cada ronda por Telegram trae hallazgos nuevos del mismo tipo.

Decisión del usuario (2026-09-30): se deja de corregir hallazgo por hallazgo. Se aceptó el
[`ADR 0014`](decisions/0014-flujo-de-un-mensaje.md) (flujo de un mensaje en seis etapas,
experimento A/B de redacción, criterios, moratoria de parches de conversación y prueba
posterior de flujo contra modelo) y se congeló la funcionalidad nueva (ver "Próximo
paso").

Gobiernan: [`product/que-es-prisma.md`](product/que-es-prisma.md), [`architecture/frontera.md`](architecture/frontera.md),
[`ROADMAP.md`](ROADMAP.md), [`capacidades.md`](capacidades.md); investigación externa en
[`research/hermes-agent.md`](research/hermes-agent.md). Superados: [`INDEX.md`](INDEX.md#documentos-superados).

## Estado comprobado

- Fundación multi-tenant con `row level security` forzado y política de aislamiento
  contra el espacio vigente: 34 tablas (recontadas el 2026-09-30 en `db/esquema.sql`:
  31 en el bucle de la línea 2104 y `absence`, `audit_log` e `incident` aparte, líneas
  2149-2160). Aislamiento entre clientes cerrado
  por las migraciones `0003` a `0005`
  ([`architecture/frontera.md`](architecture/frontera.md#cómo-se-cerró-la-regla-1));
  `PENDIENTE` un ensayo de propiedad sobre un clúster enteramente limpio (hoy se
  verifica sobre una base nueva dentro de un clúster existente).
- Sin vocabulario de cliente congelado en el esquema: `area` y `rol` son tablas con
  alcance de espacio (`db/esquema.sql:106,114`). Incorporar un segundo cliente no exige
  modificar el esquema.
- El estado de tarea es proyección de eventos, no campo editable
  (`db/esquema.sql:433,1636`).
- Superficie HTTP: `POST /telegram/{slug}`, `GET /tablero/{token}` (vista HTML por
  token) y `GET /salud` (`src/prisma/gateway.py:344,4163,4213`). No existe API de
  lectura.
- Migraciones hasta `0025` en `db/migrations/` (la `0024` exime los avisos de
  coordinación del tope diario, la `0025` es Rechazar con motivo). Cada una con
  rollback y ensayo de paridad en la suite.
- Circuitos implementados y probados en vivo por Telegram con datos ficticios en la
  cuarta ronda: entrega con evidencia y revisión (ADR 0009), aprobación que cierra la
  tarea (ADR 0008), cambios pedidos con motivo visible, alta guiada, opciones y menú por
  tarea (ADR 0007). Circuitos A y B completos; C hasta "Enviar a aprobación".
- Feature previa "Prisma orienta" (T1-T4b) cerrada; ver
  [`../odd/tasks/prisma-orienta.md`](../odd/tasks/prisma-orienta.md) y su diario en
  [`historial/`](historial/prisma-orienta-diario-hasta-2026-09-30.md).
- Git: trabajo en `main`, por delante de `origin/main` sin push (lo decide el usuario).
  Frontera de revisión RDD en `ec3109a` (rebanada de documentación aprobada y
  reconocida, linaje `review-147d7327236bfea2`).
- Rama `feat/flujo-de-un-mensaje`, worktree
  `D:\Proyectos\Prisma-PM-worktrees\flujo-de-un-mensaje`: documento
  `odd/tasks/flujo-de-un-mensaje.md` (vive en esa rama). F1 y F2 confirmadas con commit,
  F3 en curso.
- Rama auxiliar `auxiliar/alta-y-google` (worktree `alta-y-google`, alta con correo
  verificado y Google; [`ADR 0010`](decisions/0010-correo-verificado-y-google-en-el-producto.md),
  propuesta). Congelada junto con la funcionalidad nueva; le toca traer los cambios de
  `main` antes de su próxima rebanada.

## Baseline de pruebas

| Campo | Valor |
|---|---|
| Comando | `.venv\Scripts\python.exe -m pytest -q` |
| Fecha | 2026-09-30 |
| Resultado exacto | 2279 passed, 333 deselected (en `main`; los deselected son los escenarios del banco real `modelo_real`) |

Banco real completo (n=1), 2026-09-30: 108/111; las tres fallas están explicadas (dos
eran del arnés y se corrigieron en `ffe4e85`). Corridas anteriores y su detalle:
[`historial/STATUS-hasta-2026-09-30.md`](historial/STATUS-hasta-2026-09-30.md).

## Operación

- Sin producción, sin trabajo real cargado, sin Docker ni staging. Telegram real sólo
  con datos ficticios (cuentas de prueba Ariel, Ismael y Marcos).
- Base `prisma` (local): ronda 4, rearmada dos veces el 2026-09-30, esquema completo
  hasta `0025`, modelo `nan`/`deepseek-v4-flash`, Ariel administrador. **No se toca**
  hasta terminar el circuito C. Respaldo previo al flujo:
  `db/respaldos/prisma-antes-flujo-20260930.dump`.
- Base `prisma_flujo`: nueva, para la primera prueba real de la variante B; el `.env`
  del worktree `flujo-de-un-mensaje` apunta a ella.
- El listener de `main` está detenido (el usuario lo cortó con Ctrl+C) para liberar el
  bot para el listener del worktree. El listener lo corre el usuario en su propia
  terminal (`python -m prisma escuchar corework`); las tareas en segundo plano del
  agente se cortan por tiempo.
- Banco de modelos en curso sobre `main`: `deepseek/deepseek-v4-pro` y
  `anthropic/claude-sonnet-5.5` por OpenRouter, contra `deepseek-v4-flash`.
  Resultado: `PENDIENTE`.
- Quedan bases residuales `prisma_diag_*`/`prisma_test_*` de corridas viejas en el
  servidor local.

## Riesgos prioritarios

1. **El outbox está atado a un transporte.** `message_outbox` tiene `chat_id` y
   `telegram_message_id` y no tiene columna de canal (`db/esquema.sql:569,572,612`).
   Bloquea toda superficie que no sea la conversacional.
2. **Un límite de transporte decide validez de negocio.** `telegram_utf16_units`
   (`src/prisma/salida.py:103`) se usa para aceptar o rechazar datos de negocio en
   `src/prisma/ingreso_tareas.py` (uso en `:1921`; `PENDIENTE` recontar los demás).
3. **No existe grafo de transiciones de estado.** `actualizar_estado` acepta cualquier
   destino del tipo enumerado sin validar que la transición sea legítima
   (`src/prisma/herramientas.py`, `_preparar_actualizar_estado`, `:1050`).
4. **`pending_reply` no es operativo.** La tabla y la escalera existen, pero el ingreso
   no crea ni satisface el ciclo de respuesta, de modo que el seguimiento no puede
   afirmar silencio sobre evidencia real.
5. **`confirmar_borrador_tarea` fija el espacio con el valor que recibe.** Está
   acotada a `prisma_gateway` y fuera del alcance de `prisma_app`, pero confiar el
   espacio a quien llama es el patrón que la frontera rechaza.
6. **La conversación se siente robótica.** El modelo interpreta poco: fechas, objetivo
   y título del alta guiada los resuelven expresiones regulares y listas. Es lo que
   ataca el ADR 0014.

Las referencias de línea se contrastaron contra el código el 2026-09-30; se
desactualizan con cada cambio, así que conviene contrastar contra el símbolo.

## Deudas registradas

- **Revisión del contexto LLM.** Comparar calidad, completitud, costo, latencia y
  exposición del contexto amplio frente a variantes reducidas o adaptativas; requiere ADR
  antes de operar en internet.
- **Capacidades de producción.** Cola de entrada, pool de conexiones, secreto
  obligatorio de webhook, observabilidad, respaldo y restauración (horizonte posterior
  del roadmap).
- **Alta de un segundo cliente.** El mecanismo de paquetes es genérico; el proceso de
  alta no está definido.
- **Autoridad sobre `cancelada`** (T2b): `PENDIENTE` de decisión explícita.
- **Aviso por cambio de fecha** de dependencias sin disparador (la fecha objetivo es
  inmutable una vez comprometida la tarea).
- **Reintento del despachador** puede reordenar partes de una respuesta partida (límite
  documentado, no corregido).
- **`b-0005-b`**: Jev da 0,76/0,53 a "el plc", debajo de `jev.CORTE_CLARA = 0,85`;
  `PENDIENTE` de decisión de producto (umbral o contexto).
- **ADR 0007**: dos puntos abiertos en "Pendiente" (respuesta sin opciones; opciones en
  el grupo de gestión).
- **Configuración**: el resumen "Estado del equipo" va a un grupo de Telegram que no
  existe ("chat not found", un incidente; R4b-H7).
- En espera, sin descartar: cierre con el estado real en la rama de opciones y en la
  negativa sin intento (`b-0027-d`); observaciones no bloqueantes de las revisiones;
  vista previa vieja (`crear_borrador_tarea`) con Cancelar; T9-H19i; índice de
  `inbound_message`; relojes de `despachador` y `contexto`; T8d (responder en un solo
  viaje); validador de invariantes (`odd/tasks/validador-invariantes.md`); menú sin
  "Adjuntar evidencia" al aprobador. Advertencias del arnés del banco: cualquier aviso a
  otra persona respalda un "le avisé" (debería ser un aviso de coordinación a la persona
  nombrada) y en `b-0027-d` un intento rechazado de `aprobar_tarea` no debe contar como
  herramienta ejecutada.

## Próximo paso

Orden vigente (decisión del usuario, 2026-09-30). **Moratoria:** no se agregan reglas ni
parches de conversación mientras dure el experimento; los hallazgos nuevos se registran y
se clasifican por etapa del ADR 0014.

1. **Circuito C (base `prisma`).** El 01/10 a las 09:00 le llega a Ismael el borrador de
   Marcos; Ismael toca ✖️ Rechazar con un motivo y a Marcos le debe llegar "Ismael
   rechazó el borrador…: motivo". Salen además avisos encolados fuera de horario; tres
   son de «Dashboard de lotes», ya `terminada`: observar si el despachador descarta los
   que dejaron de corresponder. Es la prueba del código actual.
2. **Flujo del ADR 0014 en la rama `feat/flujo-de-un-mensaje`** (F3 en curso), acotado a
   los caminos de los hallazgos pendientes de la ronda 4, con las variantes A y B
   seleccionables por configuración del espacio. Esos hallazgos son el guion de la
   prueba, no una lista de correcciones: R4c-H3, R4b-H5, R4c-H4 a H10 (alta guiada; el
   orden "¿Qué hay que hacer?" primero sigue decidido), R4c-H1, R4c-H2, R4b-H1, R4b-H2 a
   H4. Lista con una línea por hallazgo en `odd/tasks/prisma-orienta.md`.
3. **Prueba por Telegram real**, datos ficticios y base `prisma_flujo`: el mismo guion con
   A y con B. El usuario anota por respuesta si mejoró, empeoró o quedó igual respecto de
   la ronda 4; se registran latencia, llamadas al modelo, incidentes y rechazos de la
   verificación de A.
4. **Enmienda del ADR 0014** con el resultado y extender el flujo al resto. Después, la
   prueba de seguimiento flujo contra modelo (ADR 0014).

En paralelo: banco de modelos (ver "Operación"), para saber cuánto de lo "robótico" viene
del modelo y no del flujo.

**Funcionalidad nueva congelada** hasta que alta, entrega y aprobación cumplan en una
prueba real los criterios del ADR 0014. Alcance en [`ROADMAP.md`](ROADMAP.md), "Orden de
entrega". Después, según el roadmap: aportes sobre tareas, aprendizaje de apodos y
aclaraciones, conversación de bloqueos.

**Punto exacto para retomar.** `main` con la documentación condensada en `7c2531b` (la
historia en `historial/`; frontera de revisión en `ec3109a`: el tramo de la condensación
no se pudo revisar con RDD porque las copias de historial exceden el contexto del
revisor; se verificaron por hash y una revisión independiente de los textos curados no
encontró reglas perdidas), sin push. Continuar por el punto 1 (el 01/10 a las 09:00); el punto 2 avanza
en el worktree `flujo-de-un-mensaje` leyendo primero `odd/tasks/flujo-de-un-mensaje.md`
de esa rama. Consentimiento permanente del usuario para commits y revisiones RDD; parar
sólo por decisiones sobre cómo funciona Prisma. Antes de cada unidad, el chequeo de rumbo
escrito de `AGENTS.md` ("Cómo pensamos juntos").
