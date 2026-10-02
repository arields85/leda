# Estado actual

**Alcance:** Leda es un producto de gestión de proyectos multi-tenant. CoreWork es
su primer cliente, no su definición.

**Última actualización documental:** 2026-09-29.

## Resumen

El alcance del proyecto cambió: Leda dejó de tratarse como asistente interno de un
equipo y pasó a definirse como producto ofrecible a varios clientes, con superficie
conversacional, superficie de lectura y eventual aplicación móvil.

La base documental se reescribió en consecuencia:

- [`product/que-es-leda.md`](product/que-es-leda.md) define el producto y separa
  configuración de cliente de núcleo del producto.
- [`architecture/frontera.md`](architecture/frontera.md) define dónde termina el
  núcleo y qué reglas lo gobiernan. Gobierna a los demás documentos de arquitectura.
- [`ROADMAP.md`](ROADMAP.md) ordena qué se aprovecha, qué se corrige y qué queda
  superado.

Los documentos del piloto local por fases quedaron superados y están marcados como
tales. Ver [`INDEX.md`](INDEX.md#documentos-superados).

## Estado comprobado

- La fundación multi-tenant existe y es la parte mejor construida del sistema: 28
  tablas con `row level security` forzado y política de aislamiento contra el espacio
  vigente (`db/esquema.sql:1474-1492`).
- No hay vocabulario de cliente congelado en el esquema: `area` y `rol` son tablas con
  alcance de espacio (`db/esquema.sql:106,114`), no tipos enumerados. Incorporar un
  segundo cliente no exige modificar el esquema.
- El estado de tarea es proyección de eventos, no campo editable
  (`db/esquema.sql:1231`).
- La superficie HTTP se limita a `POST /telegram/{slug}` y `GET /salud`
  (`src/leda/gateway.py:47,434`). No existe API de lectura.
- La Unidad 1A (borrador y compromiso de tarea) está implementada, verificada de forma
  independiente y fue activada en su momento sobre la base local. Su evidencia
  detallada se conserva en
  [`phases/01-local-pilot-foundations.md`](phases/01-local-pilot-foundations.md).
- Las migraciones `0001` y `0002` se ensayaron contra bases descartables, incluida
  paridad entre instalación limpia y migración, y rollback guardado. **No fueron
  aplicadas a ninguna base operativa.**
- El trabajo vive en la rama `main` (renombrada desde `master` el 2026-09-25, a
  pedido explícito del usuario). Primer push a `origin` (GitHub) el 2026-09-27, a pedido
  explícito del usuario: `main` publicada y siguiendo a `origin/main` (verificado con
  `git ls-remote --heads origin`). Antes del push se verificó que no se versiona ningún
  `.env`, respaldo ni credencial.
- Rama auxiliar `auxiliar/alta-y-google` (worktree `D:\Proyectos\Prisma-PM-worktrees\alta-y-google`,
  creada desde `main` en `dec6ae9`, 2026-09-27) para el alta con correo verificado y
  Google, agenda y reuniones: contrato en
  [`odd/tasks/alta-y-google.md`](../odd/tasks/alta-y-google.md), alcance en
  [`ADR 0010`](decisions/0010-correo-verificado-y-google-en-el-producto.md)
  (**propuesta**, la acepta el usuario). `main` no cambia de comportamiento hasta que
  el usuario decida integrarla.
- Migraciones `0013` a `0016` escritas, con rollback y ensayo de paridad en la suite;
  aplicadas limpio sobre una **copia** de la base local (experimento 1, 2026-09-27).
  **No aplicadas a la base local**: la tercera ronda usa una base nueva creada desde
  `db/esquema.sql` completo (`PRUEBA-LOCAL.md` §5).

## Baseline de pruebas

| Campo | Valor |
|---|---|
| Comando | `.venv\Scripts\python.exe -m pytest -q` |
| Fecha | 2026-09-29 |
| Resultado exacto | 1396 passed, 147 deselected (corrida del escritor de T9-R1b-3, commit `3bcaa99`; los 147 deselected son los escenarios del banco real `modelo_real`, incluidas las familias `b-0019` y `b-0020`). |

Seguimientos de la entrega con evidencia (T6a-T6j), siembra reproducible (T7, T7b) y
comprobadores del banco, `odd/tasks/leda-orienta.md`: `1008 passed, 108
deselected` (corrida aislada del escritor de T7b; cada unidad reejecutó además su
suite enfocada en el orquestador). Una falla intermitente `tuple concurrently updated`
en `tests/test_task_intake.py` apareció dos veces sólo cuando otra corrida aplicaba
el esquema en el mismo servidor a la vez (los roles son del clúster); aislada pasa.

Sesión 2 por Telegram, hallazgos 8 y 9 (entrega con evidencia y revisión, ADR
0009, `odd/tasks/leda-orienta.md`): `927 passed, 108 deselected` (216 s) --
línea base 912 (hallazgos 1-7 de la misma sesión) + 15 pruebas nuevas. Antes,
reejecutada como parte del cierre documental (T5): mismo resultado, `876
passed, 108 deselected` (206 s). La corrida de 2026-08-15
(`306 passed, 0 failed`) y la de 2026-09-24 (`721 passed, 99 deselected`, "Cerrado:
aclaración con botones" más abajo) quedan como registro histórico de una suite mucho
más chica; no reflejan el estado actual del código. Los `108 deselected` son los
escenarios del banco marcados `modelo_real` (`tests/banco/`), que no corren en la
suite por defecto.

## Correcciones anteriores

Tres ejercicios progresivos sobre Telegram se detuvieron sin crear trabajo real y
produjeron correcciones sucesivas: un circuito de alta de tareas propiedad del
servidor, un router de intención con salida tipada y validada, la reubicación del
commit del gateway fuera del bloque de espacio, y una guarda de codificación UTF-8 en
la migración `0002`. El detalle de cada corrección vive en la historia del repositorio
y en los documentos superados; no se reproduce aquí.

La conclusión que sobrevive a ese ciclo está registrada en
[`architecture/frontera.md`](architecture/frontera.md): cada corrección movió autoridad
hacia el servidor sin una decisión de arquitectura explícita, y esa frontera existe
para que la próxima corrección tenga un lugar declarado al que pertenecer.

## Operación

- El listener está detenido.
- No hay Telegram real, base operativa, Docker ni staging en uso.
- No hay datos ni trabajo real cargados.
- Los datos ficticios de las sesiones 1 y 2 viven en la base de mantenimiento
  `postgres` del servidor local (no hay una base llamada `leda`), la misma a la que
  apunta `LEDA_TEST_DB_URL`: las pruebas se conectan ahí sólo para crear y borrar sus
  bases descartables. Quedan bases residuales `leda_diag_*`/`leda_test_*` de
  corridas viejas. La tercera ronda pasa a una base dedicada nueva.

## Riesgos prioritarios

1. **El outbox está atado a un transporte.** `message_outbox` tiene `chat_id` y
   `telegram_message_id` y no tiene columna de canal (`db/esquema.sql:533,548`).
   Bloquea toda superficie que no sea la conversacional.
2. **Un límite de transporte decide validez de negocio.** `telegram_utf16_units`
   (`src/leda/salida.py:39`) se usa para aceptar o rechazar datos de negocio en
   `src/leda/ingreso_tareas.py:532,547,554,1118`.
3. **No existe grafo de transiciones de estado.** `actualizar_estado` acepta cualquier
   destino del tipo enumerado sin validar que la transición sea legítima
   (`src/leda/herramientas.py:464-491`).
4. **`pending_reply` no es operativo.** La tabla y la escalera existen, pero el ingreso
   no crea ni satisface el ciclo de respuesta, de modo que el seguimiento no puede
   afirmar silencio sobre evidencia real.
5. **`confirmar_borrador_tarea` fija el espacio con el valor que recibe.** Está
   acotada a `leda_gateway` y fuera del alcance de `leda_app`, pero confiar el
   espacio a quien llama es el patrón que la frontera rechaza. Pertenece al ingreso
   autenticado.

### Cerrado: aislamiento entre clientes

Era el riesgo número uno. Las tablas de eventos de estado no tenían `workspace_id`
ni política, y las cuatro funciones `security definer` pertenecían a `postgres`
—superusuario y `bypassrls`—, así que adentro de sus cuerpos la RLS no aplicaba.
Cerrado por las migraciones `0003` y `0004`; el detalle está en
[`architecture/frontera.md`](architecture/frontera.md#cómo-se-cerró-la-regla-1).

La migración `0005` cerró el resto: `audit_log`, `incident` y `absence` recibían
`insert` sin política. Figuraba como riesgo menor, pero lo comprobado fue que un
espacio podía **fabricar auditoría atribuida a otro**. La auditoría autoritativa es
la evidencia que se le muestra a un cliente; si otro puede escribir en ella, deja
de serlo. Su posición en la lista venía de cuando Leda era un bot de un solo
equipo y nadie más podía escribir.

`audit_log` e `incident` conservan a propósito la posibilidad de espacio nulo, para
los hechos de alcance global que sólo origina la conexión administrativa: una fila
sin espacio no queda atribuida a ningún cliente y por eso no falsifica su registro.

Queda `PENDIENTE` un ensayo de propiedad sobre un clúster enteramente limpio: hoy
se verifica sobre una base nueva dentro de un clúster existente.

## Deudas registradas

- **Revisión del contexto LLM.** Comparar calidad, completitud, costo, latencia y
  exposición del contexto amplio frente a variantes reducidas o adaptativas. No es
  todavía una política aprobada; requiere ADR antes de operar en internet.
- **Capacidades de producción.** Cola de entrada, pool de conexiones, secreto
  obligatorio de webhook, observabilidad, respaldo y restauración. Ordenadas en el
  horizonte posterior del roadmap.
- **Alta de un segundo cliente.** El mecanismo de paquetes es genérico, pero el
  proceso de alta no está definido.

## Próximo paso

**Segunda sesión real por Telegram hecha** (2026-09-27, datos ficticios, base local con
copias `db/respaldos/leda-antes-sesion2-20260927.dump` y
`leda-antes-0012-20260927.dump`; cero incidentes). Diez hallazgos, registrados en
`odd/tasks/leda-orienta.md`: los hallazgos 1 a 7 quedaron corregidos y probados en vivo
(lista de botones por unión de consultas, una sola pregunta, etiquetas cortas por palabra
sin palabra de enlace final, resumen en vez de enumerar, encabezado del menú con
responsable y estado, aprobar cierra la tarea cuando se cumplen las condiciones —
[`ADR 0008`](decisions/0008-la-aprobacion-cierra-la-tarea.md)); los hallazgos 8 y 9 se
construyeron como entrega con evidencia y revisión
([`ADR 0009`](decisions/0009-entrega-con-evidencia-y-revision.md), migración `0012`
aplicada también en la base local) y **todavía no se probaron en vivo**.

**Después de la sesión 2 (2026-09-27/28):** los seguimientos de la entrega con evidencia
quedaron cerrados y revisados (T6a-T6j, `odd/tasks/leda-orienta.md`): una aprobación
anterior no sobrevive a "Pedir cambios" (`0013`); después de "Pedir cambios" la entrega
pide evidencia nueva y la evidencia enviada se registra siempre (`0014`); "Pedir
cambios" devuelve la tarea al estado previo a la entrega aunque haya una dependencia
abierta (`0015`); el aviso de entrega no se duplica ni se pierde; una entrega repetida
sobre una tarea en revisión suma evidencia sin cambiar estado; evidencia nueva en
revisión reemplaza el aviso del aprobador; los actos sobre una misma tarea se
serializan y la hora de cada evento, evidencia y aprobación es la de escritura
(`0016`). Decisiones del usuario registradas como enmiendas de ADR 0009. Prueba de punta
a punta de "Pedir cambios" por el webhook. Todo esto **todavía no se probó en vivo**.

**Punto exacto para retomar (cierre de sesión 2026-09-30, noche).** `main` por delante de
`origin/main` (sin push; lo decide el usuario). Frontera de revisión RDD en `d4eefc7`
(`review-cb3deef4705ea11f`, aprobada y reconocida; todo el código revisado). Esa revisión
dejó dos advertencias sobre el arnés del banco para el punto 6: cualquier aviso a otra
persona respalda un "le avisé" (debería ser un aviso de coordinación a la persona
nombrada) y en `b-0027-d` hay que verificar que un intento rechazado de `aprobar_tarea` no
cuente como herramienta ejecutada.
Consentimiento permanente del usuario para las revisiones; parar sólo por decisiones sobre
cómo funciona Leda. Detalle y evidencia de todo en `odd/tasks/leda-orienta.md`.

**Cuarta ronda por Telegram (T11) en curso.** Circuito A completo de punta a punta (entrega,
cambios pedidos, reentrega, aprobación) y circuito B completo; circuito C hasta "Enviar a
aprobación". Falta: el 01/10 a las 09:00 le llega a Ismael el borrador de Marcos (quedó en
la cola por estar fuera de horario, R4b-H6); Ismael toca ✖️ Rechazar con un motivo y a Marcos le
tiene que llegar "Ismael rechazó el borrador…: motivo". A las 09:00 salen además cinco
avisos encolados fuera de horario; tres son de «Dashboard de lotes», que ya está
`terminada`: observar si el despachador descarta los que dejaron de corresponder. El
listener lo corre el usuario en su propia terminal (`.\.venv\Scripts\python.exe -m
leda escuchar corework`): las tareas en segundo plano del agente se cortan por tiempo.

**Cambio de rumbo (decisión del usuario, 2026-09-30, noche): se deja de corregir hallazgo
por hallazgo.** La capa de datos funciona, pero la conversación se siente "robótica" y
cada ronda trae hallazgos nuevos del mismo tipo. Se aceptó el
[`ADR 0014`](decisions/0014-flujo-de-un-mensaje.md): el flujo de un mensaje en seis
etapas, cada una con un solo dueño (contexto en PostgreSQL, interpretar con el modelo,
decidir con duda con Jev, garantizar con código, persistir en PostgreSQL, responder a
partir del resultado del turno). La redacción de la respuesta se decide por experimento:
**A** (el modelo redacta todo sobre el resultado, con verificación del código) frente a
**B** (plantillas para los efectos). **Moratoria:** no se agregan reglas ni parches de
conversación mientras dure el experimento; los hallazgos nuevos se registran y se
clasifican por etapa.

**Próximo, en orden:**
1. Terminar el circuito C a las 09:00 y observar los avisos viejos (prueba del código
   actual).
2. Aplicar el flujo del ADR 0014, acotado a los caminos de los hallazgos pendientes de la
   ronda 4, con las variantes A y B seleccionables por configuración del espacio. Esos
   hallazgos son el guion de la prueba, no una lista de correcciones: R4c-H3, R4b-H5,
   R4c-H4 a H10 (alta guiada; el orden "¿Qué hay que hacer?" primero sigue decidido),
   R4c-H1, R4c-H2, R4b-H1, R4b-H2 a H4.
3. Prueba por Telegram real, datos ficticios y base nueva: el mismo guion con A y con B.
   El usuario anota por respuesta si mejoró, empeoró o quedó igual respecto de la ronda 4;
   se registran latencia, llamadas al modelo, incidentes y rechazos de la verificación de A.
4. Registrar el resultado como enmienda del ADR 0014 y extender el flujo al resto.

En paralelo (decisión del usuario, 2026-09-30): el banco real sobre el código de `main`
con `deepseek/deepseek-v4-pro` y `anthropic/claude-sonnet-5.5` por OpenRouter, más una
corrida del modelo actual la misma noche, para saber cuánto de lo "robótico" viene del
modelo y no del flujo. `PENDIENTE`: resultado.

**Funcionalidad nueva congelada** (decisión del usuario, 2026-09-30) hasta que alta,
entrega y aprobación cumplan en una prueba real los criterios del ADR 0014. Alcance en
`ROADMAP.md`, "Orden de entrega".

Quedan en espera, sin descartar: cierre con el estado real en la rama de opciones y en la
negativa sin intento; observaciones no bloqueantes de las revisiones; vista previa vieja
(`crear_borrador_tarea`) con Cancelar; T9-H19i; índice de `inbound_message`; relojes de
`despachador` y `contexto`; las dos advertencias del arnés del banco (arriba).
Configuración a decidir con el usuario: el resumen "Estado del equipo" va a un grupo de
Telegram que no existe ("chat not found", un incidente; R4b-H7).

Hecho el 2026-09-30 (además de lo de la mañana): R4-H7 (las respuestas contaban contra el
tope diario y postergaban los avisos), R4-H8 (estado real con los cambios pedidos), saludo
en una línea, "Dale, escribime qué necesitás.", pregunta de evidencia real, link directo a
la vista previa, y las decisiones del usuario: avisos de coordinación fuera del tope
(precisión en `nucleo/mecanica-pm.md` §10, migración `0024`), Rechazar con motivo y aviso a
quien pidió (migración `0025`), no preguntar dos veces lo mismo, mensaje editado ignorado,
cierre con el estado real tras un cambio rechazado, íconos por acción en el menú. Suite
completa: 2279 passed, 333 deselected. Banco real completo (n=1): 108/111 (las tres fallas
explicadas; dos eran del arnés y se corrigieron en `ffe4e85`).

Cerradas en la sesión del 2026-09-28 (noche) (detalle y evidencia en
`odd/tasks/leda-orienta.md`): avisos
al administrador con espera entre reintentos y sin fallar en silencio (#28b, #28c);
administrador alcanzable en modo local (`python -m leda administrador`, `escuchar`
lee el bot de administración sin robarle un webhook ajeno; #11, #11b, #11c); una sola
rutina de fondo para `escuchar` y `servir` con cadencias releídas de la base y
`--sin-cadencias` (#29, #29b, #29c; arregló que la cadencia del lunes salía el martes);
el token del bot fuera de todo error guardado o impreso; íconos por categoría en los
botones y saludo diario al primer mensaje del día a cada persona, decidido al despachar
(#7, #7b, #7c; migraciones `0018`, `0019`); `escuchar`/`servir` se niegan a arrancar si
falta una migración; respuesta inmediata e indicador "escribiendo…" con borrador
nativo sólo si el turno pasa de 1,5 s (#9, #9b, ADR 0011).

Base local `leda` **rearmada dos veces el 2026-09-30 para la cuarta ronda** (la segunda con respaldo `db/respaldos/leda-antes-ronda4b-20260930.dump`; migraciones hasta `0025`) con datos ficticios nuevos (respaldo previo `db/respaldos/leda-antes-ronda4-20260930.dump`; esquema completo, pack, feriados, semilla ficticia, modelo `nan`/`deepseek-v4-flash`, Ariel administrador; Ariel, Ismael y Marcos activos). Antes: migraciones hasta `0023` aplicadas (`0023` el 2026-09-30, con respaldo `db/respaldos/leda-antes-0023-20260930.dump`, 532 entradas, y ensayo previo en una copia descartable; `verificar_migraciones` -> `None`) (`0020` a `0022` el 2026-09-29, con
respaldo `db/respaldos/leda-antes-0020-0022-20260929.dump` y ensayo previo en una copia
descartable; `saludo.verificar_migraciones` -> `None`); modelo `nan`/`deepseek-v4-flash`
configurado en la ronda (respaldos
`db/respaldos/leda-antes-0017-20260928.dump` y
`leda-antes-0018-0019-20260928.dump`); Ariel De Simone designado administrador de
plataforma; `LEDA_BOT_TOKEN_ADMIN` configurado y rotado por el usuario.

**Tercera ronda por Telegram hecha y cortada (2026-09-28, 21:00-21:46).** Registro
completo en `odd/tasks/leda-orienta.md` (hallazgos R3-H1 a R3-H21). Evaluación del
usuario: "tarda mucho en responder, se pierde en la conversación, no es para nada
fluido". Tres causas de fondo: la latencia del modelo (10-17 s por turno con
`nan`/`deepseek-v4-flash`; 0 s cuando decide el código), el manejo del estado de la
conversación y ninguna señal al tocar botones. El circuito A quedó cortado: la nueva
entrega después de "Pedir cambios" no volvió a revisión (R3-H20); el B no se corrió.

**Hecho el 2026-09-28/29 (detalle y evidencia en `odd/tasks/leda-orienta.md`, T8):**

- Manual de personalidad leído y contrastado con el corpus: da criterio, no mecanismo,
  para los críticos de estado; sus preguntas de cierre en texto abierto contradicen ADR
  0007 (prevalece el repo); probable causa de R3-H18 en `contexto.PREAMBULO` (obliga a
  ofrecer opciones aunque no haya opciones reales).
- **No se cambia de modelo.** NaN `deepseek-v4-flash` es la versión 4.1 y es el más
  rápido por llamada (~1 s aislada; ~2,5 s el mismo modelo por OpenRouter); Gemini 3.8
  flash fue más lento y aprobó menos escenarios; GPT-6 Luna choca con la validación del
  ruteo. La lentitud venía de las llamadas en serie de cada turno.
- Clave por proveedor (`beda9a5`); el ciclo del responder corta cuando la vuelta deja
  algo pendiente (`6c3c936`): turno mediano en el banco de ~12,6 s a ~9,4 s; tiempo
  máximo de 20 s por intento con 2 reintentos (`9818354`) contra cuelgues de ~93 s de
  NaN (~1,3 % de las llamadas). El ruteo en paralelo (ADR 0012) se probó y se revirtió
  (`ccf5c73`): poca ganancia y más cuelgues con pedidos simultáneos.
- Postergada (T8d, optimización): responder en un solo viaje cuando el dato ya está
  en el contexto; va después de T11.

**Próximo, en este orden (decisión del usuario, 2026-09-29):**

1. **Estado de la conversación (críticos, T9), por reglas generales y no por parches**
   ([`ADR 0013`](decisions/0013-reglas-generales-de-la-conversacion.md), decisión del
   usuario del 2026-09-29): pregunta pendiente como contexto con comandos cerrados (patrón
   de "conversation repair" de los asistentes de tareas, adoptado dentro del monolito),
   una respuesta visible por mensaje, estado real y sólo opciones posibles, toque con
   señal e idempotente. **Hecho (2026-09-29):** la regla 1 para el dato del menú (R1a),
   Modificar y "Ninguna, lo escribo" (R1b, R1b-2, R1b-3), con un solo manejo genérico: el
   ruteo recibe la pregunta pendiente (descripción y pregunta literal) y devuelve un
   comando de una lista cerrada; al contestar, la tarea de la pregunta es el sujeto por
   defecto; con "otro tema" el código rechaza volver a proponer lo pendiente. Banco real:
   `b-0019` 21/21, `b-0020` 17/18 (la falla restante es de redacción, T10). **Falta:**
   R1c (alta guiada), R2, R3, R4 y reproducir H19. Los hallazgos son casos de prueba: R3-H17 (un slot pendiente se traga un
   "hola" como evidencia), R3-H20 (la nueva entrega no vuelve a revisión), R3-H15 (un
   mensaje sin texto no recibe respuesta), R3-H19 (dos respuestas para un mensaje),
   R3-H18 (opciones que no se pueden cumplir), R3-H16 (el motivo de "Pedir cambios" no
   se ve), R3-H5 y R3-H13 (señal al tocar botones; doble toque en silencio).
2. **Forma de las respuestas (T10):** R3-H1 (aviso de incidente con explicación humana,
   formato aprobado), R3-H2 (mensaje neutro nuevo, texto aprobado), R3-H3/H7 (regla de
   lista), R3-H8 ("hola" suelto), R3-H9 ("Gracias. La tarea pasó a revisión."),
   R3-H10, R3-H11, R3-H12, R3-H14, R3-H4.
3. **Cuarta ronda por Telegram** (T11), en horario laboral, con los circuitos A y B.
4. **Después de T11, mejoras y optimizaciones**: T8d y lo que sigue abajo. La prioridad
   es que Leda responda y se comporte como se espera (decisión del usuario, 2026-09-29).

Después, sin bloquear: #23 validador de invariantes
(`odd/tasks/validador-invariantes.md`); escenarios del banco que fallan desde antes de
`b-0005-b` (`b-0001`, `b-0001-a`, `b-0002-c`, `b-0013`); T7d (`sembrar`); espera entre
reintentos en `message_outbox` (`despachador._fallo`); confirmación del bot de
administración al vincularse; `_activacion` sin commit explícito en /start sin token;
menores de las revisiones del saludo y del indicador en `servir`.

La rama auxiliar `auxiliar/alta-y-google` avanza en su sesión (alta con correo y
Google); `main` cambió mucho desde que se creó, así que le toca traer los cambios de
`main` antes de su próxima rebanada.

Abierto, sin bloquear:

- **Autoridad sobre `cancelada`** (T2b): no se resolvió si una autoridad superior al
  responsable puede cancelar una tarea ajena. `PENDIENTE` de decisión explícita.
- El menú de tarea (T2) todavía no ofrece "Adjuntar evidencia" al aprobador, aunque
  `herramientas.py` ya se lo permite desde T2b — ajuste de UX pendiente.
- `b-0005-b` (banco real, 2026-09-26): Jev resuelve "el plc" a 0,76/0,53 de
  probabilidad/confianza, debajo de `jev.CORTE_CLARA = 0,85`, y Leda abre una
  aclaración que el escenario no contesta — comportamiento del modelo contra un umbral
  ya codificado, no un defecto de Leda. `PENDIENTE` de decisión de producto: ajustar
  el umbral o enriquecer el contexto que recibe Jev para referencias informales de una
  sola palabra clave.
- El reintento del despachador puede reordenar las partes de una respuesta partida:
  el orden estrictamente creciente que garantiza `salida.enqueue_outbox` vale para la
  primera pasada, no para una parte reprogramada tras un fallo — límite documentado en
  `odd/tasks/leda-orienta.md`, no corregido.
- ADR 0007 sigue con dos puntos abiertos en "Pendiente": si una respuesta puede cerrar
  sin ninguna opción, y cómo se ven las opciones en el grupo de gestión.

Después de T5, según [`ROADMAP.md`](ROADMAP.md): **Aportes sobre tareas** (depende de
Leda orienta), después aprendizaje de apodos y aclaraciones, y la conversación de
bloqueos (mecánica §8, pasos 2 a 7).

El resto del orden de trabajo está en [`ROADMAP.md`](ROADMAP.md).

## Cerrado: Leda orienta (T1-T4b)

Feature `odd/tasks/leda-orienta.md`, origen [`ADR 0007`](decisions/0007-leda-orienta-no-charla.md);
acciones por tarea en
[`architecture/interpretacion-y-confirmacion.md`](architecture/interpretacion-y-confirmacion.md)
§4.6. Construido sobre `main` (commits `c253d27` a `9681973`), cada unidad con su
revisión RDD; detalle completo, decisiones y evidencia de cada corrección en
`odd/tasks/leda-orienta.md`.

- **T1 — Opciones del modelo.** `ofrecer_opciones` (`herramientas.py`): el modelo pide
  una elección con hasta `MAX_OPCIONES_MODELO = 4` opciones (texto o tarea), el
  servidor valida cada tarea contra PostgreSQL bajo RLS y arma botones más "Quiero
  consultar otra cosa"; tocar una tarea la retoma resuelta, sin pasar por Jev.
- **T2 — Menú de tarea.** `menu_tarea.calcular_menu` decide las acciones según estado y
  relación (responsable, aprobador, otra persona) del diseño §4.6; cada acción que
  cambia algo pasa por la vista previa de siempre (ADR 0005).
- **T2b — Autoridad sobre tareas ajenas.** `actualizar_estado`, `registrar_bloqueo`
  (sólo el responsable) y `adjuntar_evidencia` (responsable o aprobador) verifican
  autoridad por tarea, no sólo por rol — cerraba un hueco real observado en la sesión
  del 2026-09-25. `cancelada` queda sin resolver (arriba, "Próximo paso").
- **T3 — Listas como botones.** El servidor agrega un botón por tarea a cualquier
  respuesta que liste tareas (`consultar_tareas`), con páginas de 4 y "Ver más"; no
  depende de que el modelo llame a ninguna herramienta.
- **T4 — Banco.** `tests/banco/` gana `toques` genéricos (tocar por etiqueta o índice),
  el comprobador `comprobar_pregunta_con_opciones` (activo por defecto: si Leda
  pregunta, tiene que ofrecer botones) y tres escenarios nuevos (`b-0016` a `b-0018`).
  Corridas guionadas ejercitan el circuito lista → menú → acción → vista previa de
  punta a punta sin modelo real.
- **T4b — Cierre genérico sin opciones concretas.** Si el turno cierra preguntando en
  texto abierto sin ningún juego de botones propio, el servidor agrega "Es una tarea
  nueva" / "Es sobre una tarea existente" / "Quiero consultar otra cosa"
  (`deteccion_pregunta.py`, `agente.py`).
- **Trazabilidad de incidentes** (migración `0011`): toda falla no manejada al
  procesar un mensaje o un toque revierte, registra un incidente con etapa, referencia
  a `inbound_message`/`pending_action`, persona y chat, y avisa con un texto neutro;
  `notificado_en` sólo se completa si el aviso se encoló y confirmó de verdad.
- Además, ocho correcciones de seguimiento sobre revisiones ya aprobadas (auditoría
  fiel de un rechazo de `preparar` como `herramienta_rechazada:<nombre>`, nunca como
  ejecutado; un solo juego de botones por turno; falsos positivos de la detección de
  pregunta con URLs y subcadenas; el banco resolviendo contra la unión de acciones
  pendientes en vez de adivinar por orden) y la corrección de credenciales fuera del
  `repr` de `ClienteJev`/`Config`.

**Pruebas:** suite por defecto, 2026-09-26, `.venv/Scripts/python.exe -m pytest -q` →
**876 passed, 108 deselected** (línea base de T1 era 721 passed, 99 deselected,
2026-09-24 — ver "Baseline de pruebas" arriba).

**Banco real** (NaN `deepseek-v4-flash`, `--banco-n 3`), corrida final 2026-09-26
(`tests/banco/reportes/banco-20260926T155611Z.json`): **84 aprobado, 3 falla,
21 no_concluyente, 0 bloqueado, de 108** (36 escenarios × 3). La única falla es
`b-0005-b` (arriba, "Próximo paso"). Referencia de inicio de sesión, 2026-09-24
(`banco-20260924T225944Z.json`): 75 aprobado / 96 no-falla de 99. El proveedor `nan`
tuvo una caída real entre 2026-09-26 ~03:00Z y ~06:24Z (todo `chat completion`
devolvía 404, incluso con una clave inválida — falla del proveedor, no de la cuenta);
el banco ahora califica `bloqueado` una corrida así en vez de darla por aprobada sin
que ningún modelo haya decidido nada.

## Cerrado: aclaración con botones

Feature `odd/tasks/aclaracion-con-botones.md`. El enrutador separa las referencias;
Jev (TypeSafe vía OpenRouter) decide a qué tarea activa del espacio se refiere cada
una, con la pregunta de verificación, la de la segunda candidata y las causas de los
bloqueos abiertos a la vista; ante la duda, botones con cada candidata, "Es una tarea
nueva" y "Ninguna, lo escribo"; sin clave o con Jev caído, pregunta y registra un
incidente; toda respuesta sobre una tarea resuelta nombra su título
([`ADR 0006`](decisions/0006-jev-para-resolver-referencias-e-intencion.md), diseño §5.6
a §5.12).

Banco con modelo real y Jev real (NaN `deepseek-v4-flash`, 33 escenarios x 3, base
descartable de pruebas), 2026-09-24, cinco corridas mientras se corregía lo que
mostraba cada una: 58, 77, 84, 81 y **96 de 99** aprobadas. Las 3 que fallan son
`b-0005-b`: Jev da 0,79 a 0,84 a "el plc" (corte 0,85) y Leda pregunta; es una
pregunta de más, segura. Límites conocidos: "lo del tablero" (`b-0008`) puede elegirse
solo, lo frena la vista previa; ante algo que no existe, Leda ofrece la tarea
parecida en lugar de decir que no la encuentra. Con los 60 mensajes de los lotes,
Leda pregunta en uno de cada tres; los lotes son difíciles a propósito y la
proporción real se mide en la sesión por Telegram.

Suite por defecto, 2026-09-24: `.venv/Scripts/python.exe -m pytest -q` → 721 passed,
99 deselected.

## Cerrado: vista previa y confirmación de todo cambio

Feature `odd/tasks/vista-previa-y-confirmacion.md` (commits `2bd2200`, `763b427` y el
de cierre). Las 8 herramientas que escriben muestran estado vigente y cambio propuesto
y esperan Confirmar, Modificar o Cancelar; al confirmar se recalcula una huella del
estado y, si cambió, no se aplica. Modificar acepta la corrección durante 30 minutos.
El banco toca Confirmar por el mismo camino que Telegram y falla si alguna de las 8
herramientas se ejecutó o cambió la base antes del toque.

Verificación, 2026-09-24: `.venv/Scripts/python.exe -m pytest -q` → 536 passed, 90
deselected; `tests/banco` → 124 passed. El banco con el modelo real no se volvió a
correr con este cambio. Pendiente conocido: un ciclo de dependencias se detecta recién
al confirmar (lo frena la base), no en la vista previa.

## Cerrado: banco conversacional con el modelo real

`tests/banco/` (feature `odd/tasks/banco-conversacional.md`). Cómo se corre, en
[`docs/validation/README.md`](validation/README.md). Primera corrida real, 2026-09-23,
NaN `deepseek-v4-flash`, 7 escenarios × 10 corridas, base descartable de pruebas:

| Escenario | Aprobadas | Nota |
|---|---|---|
| b-0001 consulta de tareas propias | 10/10 | |
| b-0002 registrar un bloqueo relatado vagamente | 10/10 | |
| b-0003 resolver un bloqueo | 9/10 | la falla era del comprobador, corregido |
| b-0004 pasar una tarea a revisión | 10/10 | |
| b-0005 declarar una dependencia | 0/10 | defecto real del router, abierto |
| b-0006 pedir una tarea nueva | 10/10 | |
| b-0007 persona que no está en el equipo | 9/10 + 1 no concluyente | el no concluyente era del comprobador, corregido |

Latencia por corrida, línea base sin umbral: mediana 8,1 s, mínima 1,2 s, máxima
100,7 s (un pico aislado en `b-0002`). Suite por defecto: 473 passed, el banco no
corre en ella.

Entorno local: PostgreSQL 18.6 instalado con scoop, sin servicio de Windows; se levanta
con `levantar-postgres.bat`. Modelo activo `nan / deepseek-v4-flash`.

## Cerrado: dependencias entre tareas

Era el próximo paso anterior. `crear_dependencia`/`quitar_dependencia`
(`src/leda/herramientas.py`) crean y quitan con la autoridad decidida —responsable de
cualquiera de las dos tareas, o su referente— y avisan a la otra parte y, entre áreas
distintas, a los dos referentes; un ciclo lo rechaza `trg_evitar_ciclo_dependencia` con
un mensaje legible. El freno de `en_curso` vive en la base
(`motivo_no_arranca_tarea`/`trg_exigir_dependencias_resueltas`, migración `0008` con su
rollback). El aviso en cadena por atraso o por fecha corrida corre en la misma pasada
que la escalera (`escalera.evaluar_dependencias_en_riesgo`), deduplicado por
(origen, su fecha objetivo vigente) por destinatario. La dependencia informativa avisa a
las dos partes cuando la origen cambia de estado; el aviso por cambio de fecha queda sin
disparador porque `bloquear_estado_directo` vuelve `fecha_objetivo` inmutable una vez
comprometida la tarea y ninguna ruta de código la cambia — deuda registrada, no
implementada.
