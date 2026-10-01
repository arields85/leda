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
- Banco real de modelos sobre `main` (2026-09-30, n=1, 111 escenarios; reportes en
  `tests/banco/reportes/banco-20260930T235543Z.json` y siguientes): pasan `deepseek-v4-flash`
  110, `deepseek/deepseek-v4-pro` 87, `openai/gpt-5.6-sol` 43 y
  `anthropic/claude-sonnet-5.5` 7. **No mide comprensión, mide acople al contrato del
  ruteo:** pro no llama al ruteo exactamente una vez (17 bloqueados), sol pone propuestas
  de tarea fuera del alta (67), y Sonnet rechaza el `tool_choice` forzado de
  `llm.py:392,626` (104, infraestructura). Las fallas "de contenido" de pro y sol parecen
  respuestas razonables que el comprobador no acepta. Conclusión: el sistema y el banco
  quedaron ajustados al comportamiento de flash, y la pregunta "¿cuánto aporta el
  modelo?" sigue sin respuesta. Una comparación justa exige un ruteo que no dependa de
  las particularidades de un modelo (`PENDIENTE`, después del experimento A/B; no es
  funcionalidad nueva). La latencia del banco es por escenario (mediana de flash 13 s),
  no por respuesta: el criterio de 5 s del ADR 0014 necesita la medición por respuesta de
  F6a.
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

Orden vigente (2026-10-01). **Moratoria:** no se agregan reglas ni parches de
conversación de caso; los hallazgos se registran y se clasifican por etapa del ADR 0014.

1. **Circuito C (base `prisma`, código de `main`), corrido el 01/10 a las 09:00: no se
   pudo hacer, y dejó tres hallazgos del código de `main`.**
   - **C-1 (falla silenciosa, alta).** La vista previa de aprobación del borrador de Marcos
     vence 8 h después de crearse (creada 30/09 18:19, venció 01/10 02:19), pero quedó
     retenida por estar fuera del horario laboral hasta las 09:00; al salir ya estaba
     vencida y el despachador la descartó sin avisar a nadie (`despachador.py:572-586`).
     Marcos sigue creyendo que se la mandó a Ismael. Contradice "nunca fallar en
     silencio".
   - **C-2.** Los avisos encolados que dejaron de corresponder salen igual: a Ariel
     "pidió cambios" y "aprobó" de «Dashboard de lotes» (ya `terminada`), y a Ismael
     "entregó" con Aprobar / Pedir cambios sobre esa tarea terminada y sobre «Revisar
     comunicaciones…», donde él ya había pedido cambios.
   - **C-3.** Tocar "Aprobar" en el aviso viejo no tuvo efecto (la tarea sigue `terminada`;
     bien), pero respondió "Ese pedido ya no está vigente. Si sigue haciendo falta,
     escribime y lo vemos de nuevo.": un callejón sin salida, contra "ningún mensaje deja a
     la persona sin un próximo paso".
   El rechazo con motivo queda por probar con un borrador nuevo.
2. **Alta conducida por el modelo (rama `feat/flujo-de-un-mensaje`, base
   `prisma_flujo`).** Decisión del usuario del 01/10 (enmienda del
   [`ADR 0014`](decisions/0014-flujo-de-un-mensaje.md) "el alta conducida por el
   modelo"): la prueba de la mañana mostró que el alta seguía trabada (formulario de un
   campo por turno, ruteo y redacción sin ver la conversación, "Dejarlo" borraba el
   trabajo). Ya está en la rama: historial a los modelos, "Dejarlo" pausa, modelo puro
   sin plazo ni plantillas (`MODELO_PURO`), M1 (contrato del turno,
   `src/prisma/alta_turno.py`, `16fa0ff`), M2 (llamada `conducir_alta` en los
   proveedores, `03263de`) y **M3** (el alta conducida de punta a punta detrás de
   `workspace_setting` `alta = conversada`, `src/prisma/alta_conducida.py`, `deaade0`;
   guion "Corrida conversada" de 15 pasos en el guion de la rama, `271e462`).
   Verificación de M3 **parcial**: suite completa 3195 passed, 2 failed (una corregida en
   el mismo commit, `test_capacidades`; la otra preexistente e intermitente,
   `test_redaccion_modelo_puro::test_si_el_verificador_rechaza…`, pasa sola); falta
   repetir la suite completa. M1-M3 sin revisión RDD todavía (tramo
   `b7ed862..271e462`). Para activar en `prisma_flujo`:
   `insert into workspace_setting (workspace_id, clave, valor) select id, 'alta',
   '"conversada"'::jsonb from workspace where slug = 'corework' on conflict
   (workspace_id, clave) do update set valor = excluded.valor;` (apagar: borrar la fila o
   `'"guiada"'`). Decisiones abiertas del usuario: tope de 7 botones por dato (el modelo
   conoce hasta 40 opciones); si el alta conducida necesita un equivalente de
   `MODELO_PURO=False`.
3. **Medir y decidir.** Latencia por respuesta contra la línea base (8,7 s de mediana en
   textos), turnos por tarea, lo que entiende mal, incidentes. Si cumple: retirar el
   formulario viejo del alta (M4-M9) y extender el patrón a entrega y aprobación.
4. **Hallazgos del circuito C (código de `main`):** C-1 a C-3 (arriba) y repetir el
   rechazo con motivo con un borrador nuevo.

Lectura de las pruebas: `python tools/leer_conversacion.py [minutos] [desde HH:MM]`
(con `PYTHONPATH=src` desde el worktree para `prisma_flujo`) muestra la conversación con
los botones ofrecidos y la etiqueta de cada toque; no sacar conclusiones sin los botones.

**Funcionalidad nueva congelada** hasta que alta, entrega y aprobación cumplan en una
prueba real los criterios del ADR 0014. Alcance en [`ROADMAP.md`](ROADMAP.md), "Orden de
entrega". Después, según el roadmap: aportes sobre tareas, aprendizaje de apodos y
aclaraciones, conversación de bloqueos.

**Punto exacto para retomar (cierre de sesión 2026-10-01, ~10:45).** `main` sin push
(sólo documentación y `tools/leer_conversacion.py` desde la ronda 4; el código de `main`
sigue siendo el de la ronda 4). La rama `feat/flujo-de-un-mensaje` lleva todo el
experimento, revisado con RDD hasta `b7ed862` (`review-497ccb005edb819a`); M1 y M2
(`16fa0ff`, `03263de`) y lo que haya dejado M3 quedan por revisar. Base `prisma_flujo`:
migraciones `0026` y `0027` aplicadas (respaldos en `db/respaldos/`), áreas asignadas a
los objetivos, variante A, `alta = conversada` todavía sin activar. Base `prisma`: la de
la ronda 4, sin migraciones nuevas. Listeners detenidos. Lista de tareas de la sesión:
historial OK, M1 OK, M2 OK, M3 OK (verificación parcial), después suite completa y revisión, prueba conversada, M4-M9,
hallazgos del circuito C. Consentimiento permanente para commits y revisiones RDD;
chequeo de rumbo escrito antes de cada unidad (`AGENTS.md`).