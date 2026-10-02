# Estado actual

**Alcance:** Leda es un producto de gestión de proyectos multi-tenant. CoreWork es
su primer cliente, no su definición.

**Última actualización documental:** 2026-10-02.

Historia de sesiones y unidades cerradas:
[`historial/STATUS-hasta-2026-09-30.md`](historial/STATUS-hasta-2026-09-30.md)
(copia literal de este documento antes de su condensación).

## Resumen

Leda se define como producto ofrecible a varios clientes, con superficie
conversacional, superficie de lectura y eventual aplicación móvil. La capa de datos
funciona (sabe con quién habla, no mezcla tareas de otras personas, los flujos de alta,
entrega y aprobación avanzan de punta a punta), pero la conversación se siente
"robótica" y cada ronda por Telegram trae hallazgos nuevos del mismo tipo.

Decisión del usuario (2026-09-30): se deja de corregir hallazgo por hallazgo. Se aceptó el
[`ADR 0014`](decisions/0014-flujo-de-un-mensaje.md) (flujo de un mensaje en seis etapas,
experimento A/B de redacción, criterios, moratoria de parches de conversación y prueba
posterior de flujo contra modelo) y se congeló la funcionalidad nueva (ver "Próximo
paso").

Gobiernan: [`product/que-es-leda.md`](product/que-es-leda.md), [`architecture/frontera.md`](architecture/frontera.md),
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
  token) y `GET /salud` (`src/leda/gateway.py:344,4163,4213`). No existe API de
  lectura.
- Migraciones hasta `0025` en `db/migrations/` (la `0024` exime los avisos de
  coordinación del tope diario, la `0025` es Rechazar con motivo). Cada una con
  rollback y ensayo de paridad en la suite.
- Circuitos implementados y probados en vivo por Telegram con datos ficticios en la
  cuarta ronda: entrega con evidencia y revisión (ADR 0009), aprobación que cierra la
  tarea (ADR 0008), cambios pedidos con motivo visible, alta guiada, opciones y menú por
  tarea (ADR 0007). Circuitos A y B completos; C hasta "Enviar a aprobación".
- Feature previa "Leda orienta" (T1-T4b) cerrada; ver
  [`../odd/tasks/leda-orienta.md`](../odd/tasks/leda-orienta.md) y su diario en
  [`historial/`](historial/leda-orienta-diario-hasta-2026-09-30.md).
- Git: el 2026-10-01 se subieron `main`, el tag `pre-renombre-leda` y las ramas
  `feat/flujo-de-un-mensaje`, `feat/flujo-variante-a` y `auxiliar/alta-y-google`, como
  respaldo antes del renombre a Leda. El porqué, lo que quedó local y la limpieza
  posterior están en [`../odd/tasks/renombre-a-leda.md`](../odd/tasks/renombre-a-leda.md).
  Lo posterior al tag (el renombre en `main` y en la rama de flujo) todavía no se subió:
  lo decide el usuario. Frontera de revisión RDD en `ec3109a` (rebanada de documentación aprobada y
  reconocida, linaje `review-147d7327236bfea2`).
- Rama `feat/flujo-de-un-mensaje`, worktree
  `D:\Proyectos\Prisma-PM-worktrees\flujo-de-un-mensaje`: documento
  `odd/tasks/flujo-de-un-mensaje.md` (vive en esa rama). F1 y F2 confirmadas con commit,
  F3 en curso.
- Rama auxiliar `auxiliar/alta-y-google` (worktree `alta-y-google`, alta con correo
  verificado y Google; [`ADR 0010`](decisions/0010-correo-verificado-y-google-en-el-producto.md),
  propuesta). Congelada junto con la funcionalidad nueva; tiene trabajo avanzado que se
  integra a `main`. Antes de su próxima rebanada le toca el renombre a Leda y traer `main`,
  con el procedimiento de R12 en [`../odd/tasks/renombre-a-leda.md`](../odd/tasks/renombre-a-leda.md)
  (su `.env` apunta a la base `prisma`, que ya no existe).

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
- Renombre a Leda ([ADR 0015](decisions/0015-renombre-del-producto-a-leda.md)): el
  código renombrado usa bases nuevas, armadas desde el esquema renombrado. `leda` es para
  el código de `main` y `leda_flujo` para la rama de flujo. Las bases anteriores,
  `prisma` y `prisma_flujo`, y sus roles `prisma_*` quedan intactos como respaldo hasta
  la limpieza. **Leda funciona correctamente desde el 2026-10-02**: suites en verde
  (`main` 2286, flujo 3432), verificación byte a byte, alta real de punta a punta sobre
  `leda_flujo` y nada lee los nombres viejos. El renombre está en `main` (`2d56952`) y en
  la rama de flujo. Falta la limpieza (R11), según la tabla de
  [`../odd/tasks/renombre-a-leda.md`](../odd/tasks/renombre-a-leda.md).
- PostgreSQL local (scoop) no es un servicio: después de reiniciar la PC hay que
  levantarlo con `levantar-postgres.bat`.
- Base `prisma` (respaldo): ronda 4, rearmada dos veces el 2026-09-30, esquema hasta
  `0025`, Ariel administrador. Tiene el estado del circuito C (hallazgos C-1 a C-3 en
  "Próximo paso"). Respaldo previo al flujo:
  `db/respaldos/prisma-antes-flujo-20260930.dump`.
- Base `prisma_flujo` (respaldo): historial de las pruebas del alta conducida hasta el
  2026-10-01. `leda_flujo` la reemplaza para la rama, con los mismos ajustes
  (`alta = conversada`, `stream = true`).
- El listener de `main` está detenido (el usuario lo cortó con Ctrl+C) para liberar el
  bot para el listener del worktree. El listener lo corre el usuario en su propia
  terminal (`python -m leda escuchar corework`); las tareas en segundo plano del
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
- Bases en el servidor local (2026-10-02): `leda` y `leda_flujo`. `prisma` y `prisma_flujo`
  se borraron después de un volcado final (`db/respaldos/*-final-antes-de-borrar-20261002.dump`).
  El esquema `prisma` viejo de la base `postgres` (sesiones 1 y 2) y los roles `prisma_*`
  también se borraron, con volcado previo. En el servidor sólo quedan los roles `leda_*`.

## Riesgos prioritarios

1. **El outbox está atado a un transporte.** `message_outbox` tiene `chat_id` y
   `telegram_message_id` y no tiene columna de canal (`db/esquema.sql:569,572,612`).
   Bloquea toda superficie que no sea la conversacional.
2. **Un límite de transporte decide validez de negocio.** `telegram_utf16_units`
   (`src/leda/salida.py:103`) se usa para aceptar o rechazar datos de negocio en
   `src/leda/ingreso_tareas.py` (uso en `:1921`; `PENDIENTE` recontar los demás).
3. **No existe grafo de transiciones de estado.** `actualizar_estado` acepta cualquier
   destino del tipo enumerado sin validar que la transición sea legítima
   (`src/leda/herramientas.py`, `_preparar_actualizar_estado`, `:1050`).
4. **`pending_reply` no es operativo.** La tabla y la escalera existen, pero el ingreso
   no crea ni satisface el ciclo de respuesta, de modo que el seguimiento no puede
   afirmar silencio sobre evidencia real.
5. **`confirmar_borrador_tarea` fija el espacio con el valor que recibe.** Está
   acotada a `leda_gateway` y fuera del alcance de `leda_app`, pero confiar el
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

1. **Circuito C (base `prisma`, anterior al renombre; código de `main`), corrido el 01/10 a las 09:00: no se
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
2. **Alta conducida por el modelo: primera prueba real hecha (01/10), favorable.** Rama
   `feat/flujo-de-un-mensaje`, base `leda_flujo` con `alta = conversada` activado.
   Resultado y **criterios de adopción** en la enmienda del
   [`ADR 0014`](decisions/0014-flujo-de-un-mensaje.md) "Resultado de la primera prueba
   del alta conducida": ningún hallazgo de comprensión; 83 % de los turnos del modelo
   aceptados al primer intento (90 % desde la corrección del verificador); textos 13,0 s
   de mediana por respuesta pero menos turnos por tarea (el usuario prioriza fluidez,
   después latencia). Correcciones del día, todas revisadas con RDD por tramos y
   registradas con su evidencia en `odd/tasks/flujo-de-un-mensaje.md`: propuesta de
   criterio con un solo camino, verificador sólo con invariantes (sin "?"), hechos con el
   botón real y la regla de fechas, margen de 2 meses por espacio (`horizonte_tarea`),
   aviso al aprobar un borrador y nombre de quien lo manda. Suite completa en `13c7ae5`:
   3285 passed.
3. **Próxima prueba: la de adopción** (sin fecha: hoy no hay quien no conozca el guion; mientras tanto se avanza con los pendientes del traspaso). Por Telegram real, con alguien que no conozca el
   guion y al menos tres altas. Si cumple los criterios del ADR 0014, retirar el alta
   guiada (M4-M9) y pasar el patrón a entrega y aprobación. Pendientes de la rama antes o
   durante esa prueba: (a) y (f) el modelo promete lo que no existe ("la retomamos el
   lunes", "lo tomamos como objetivo"); (b) el borrador pausado no lo ve el camino
   general y deja una aclaración trabada; (e) alguien de Dirección recibe el objetivo
   estratégico completado solo; (g) el indicador "escribiendo…" se corta; evidencia con
   claves internas ("explicacion"); calidad del criterio aceptado ("envío videos").
4. **Hallazgos del circuito C (código de `main`):** C-1 a C-3 (arriba) y repetir el
   rechazo con motivo con un borrador nuevo.

Lectura de las pruebas: `python tools/leer_conversacion.py [minutos] [desde HH:MM]`
(con `PYTHONPATH=src` desde el worktree para `leda_flujo`) muestra la conversación con
los botones ofrecidos y la etiqueta de cada toque; no sacar conclusiones sin los botones.

**Funcionalidad nueva congelada** hasta que alta, entrega y aprobación cumplan en una
prueba real los criterios del ADR 0014. Alcance en [`ROADMAP.md`](ROADMAP.md), "Orden de
entrega". Después, según el roadmap: aportes sobre tareas, aprendizaje de apodos y
aclaraciones, conversación de bloqueos.

**Punto exacto para retomar (cierre del 2026-10-01).** Leer primero el traspaso
[`traspaso/2026-10-01-alta-conducida.md`](traspaso/2026-10-01-alta-conducida.md): el diseño
que funciona, cómo se trabajó, cómo operar y leer una prueba, decisiones del usuario,
pendientes en orden y lecciones. Primeros pasos: (1) suite completa en la rama
`feat/flujo-de-un-mensaje` (última registrada: 3411 passed en `5cd32b6`; HEAD `96a139b`
verificado con pruebas enfocadas); (2) RDD de `39bbf59..HEAD` con
`tools/rdd_por_tramos.py`; (3) preguntarle al usuario la decisión (e), qué hace el alta
cuando quien escribe es de Dirección y no tiene objetivos operativos. `main` sin push:
sólo documentación y herramientas (`tools/leer_conversacion.py --completo`,
`tools/leer_turnos_alta.py`, `tools/rdd_por_tramos.py`). Base `leda_flujo`: `alta =
conversada` y `stream` activados. Consentimiento permanente para commits y revisiones RDD;
chequeo de rumbo escrito antes de cada unidad (`AGENTS.md`).