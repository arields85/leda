# Estado actual

**Alcance:** Prisma es un producto de gestión de proyectos multi-tenant. CoreWork es
su primer cliente, no su definición.

**Última actualización documental:** 2026-09-28.

## Resumen

El alcance del proyecto cambió: Prisma dejó de tratarse como asistente interno de un
equipo y pasó a definirse como producto ofrecible a varios clientes, con superficie
conversacional, superficie de lectura y eventual aplicación móvil.

La base documental se reescribió en consecuencia:

- [`product/que-es-prisma.md`](product/que-es-prisma.md) define el producto y separa
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
  (`src/prisma/gateway.py:47,434`). No existe API de lectura.
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
| Fecha | 2026-09-28 |
| Resultado exacto | 1042 passed, 108 deselected (corrida del escritor de #28c). |

Seguimientos de la entrega con evidencia (T6a-T6j), siembra reproducible (T7, T7b) y
comprobadores del banco, `odd/tasks/prisma-orienta.md`: `1008 passed, 108
deselected` (corrida aislada del escritor de T7b; cada unidad reejecutó además su
suite enfocada en el orquestador). Una falla intermitente `tuple concurrently updated`
en `tests/test_task_intake.py` apareció dos veces sólo cuando otra corrida aplicaba
el esquema en el mismo servidor a la vez (los roles son del clúster); aislada pasa.

Sesión 2 por Telegram, hallazgos 8 y 9 (entrega con evidencia y revisión, ADR
0009, `odd/tasks/prisma-orienta.md`): `927 passed, 108 deselected` (216 s) --
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
  `postgres` del servidor local (no hay una base llamada `prisma`), la misma a la que
  apunta `PRISMA_TEST_DB_URL`: las pruebas se conectan ahí sólo para crear y borrar sus
  bases descartables. Quedan bases residuales `prisma_diag_*`/`prisma_test_*` de
  corridas viejas. La tercera ronda pasa a una base dedicada nueva.

## Riesgos prioritarios

1. **El outbox está atado a un transporte.** `message_outbox` tiene `chat_id` y
   `telegram_message_id` y no tiene columna de canal (`db/esquema.sql:533,548`).
   Bloquea toda superficie que no sea la conversacional.
2. **Un límite de transporte decide validez de negocio.** `telegram_utf16_units`
   (`src/prisma/salida.py:39`) se usa para aceptar o rechazar datos de negocio en
   `src/prisma/ingreso_tareas.py:532,547,554,1118`.
3. **No existe grafo de transiciones de estado.** `actualizar_estado` acepta cualquier
   destino del tipo enumerado sin validar que la transición sea legítima
   (`src/prisma/herramientas.py:464-491`).
4. **`pending_reply` no es operativo.** La tabla y la escalera existen, pero el ingreso
   no crea ni satisface el ciclo de respuesta, de modo que el seguimiento no puede
   afirmar silencio sobre evidencia real.
5. **`confirmar_borrador_tarea` fija el espacio con el valor que recibe.** Está
   acotada a `prisma_gateway` y fuera del alcance de `prisma_app`, pero confiar el
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
de serlo. Su posición en la lista venía de cuando Prisma era un bot de un solo
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
copias `db/respaldos/prisma-antes-sesion2-20260927.dump` y
`prisma-antes-0012-20260927.dump`; cero incidentes). Diez hallazgos, registrados en
`odd/tasks/prisma-orienta.md`: los hallazgos 1 a 7 quedaron corregidos y probados en vivo
(lista de botones por unión de consultas, una sola pregunta, etiquetas cortas por palabra
sin palabra de enlace final, resumen en vez de enumerar, encabezado del menú con
responsable y estado, aprobar cierra la tarea cuando se cumplen las condiciones —
[`ADR 0008`](decisions/0008-la-aprobacion-cierra-la-tarea.md)); los hallazgos 8 y 9 se
construyeron como entrega con evidencia y revisión
([`ADR 0009`](decisions/0009-entrega-con-evidencia-y-revision.md), migración `0012`
aplicada también en la base local) y **todavía no se probaron en vivo**.

**Después de la sesión 2 (2026-09-27/28):** los seguimientos de la entrega con evidencia
quedaron cerrados y revisados (T6a-T6j, `odd/tasks/prisma-orienta.md`): una aprobación
anterior no sobrevive a "Pedir cambios" (`0013`); después de "Pedir cambios" la entrega
pide evidencia nueva y la evidencia enviada se registra siempre (`0014`); "Pedir
cambios" devuelve la tarea al estado previo a la entrega aunque haya una dependencia
abierta (`0015`); el aviso de entrega no se duplica ni se pierde; una entrega repetida
sobre una tarea en revisión suma evidencia sin cambiar estado; evidencia nueva en
revisión reemplaza el aviso del aprobador; los actos sobre una misma tarea se
serializan y la hora de cada evento, evidencia y aprobación es la de escritura
(`0016`). Decisiones del usuario registradas como enmiendas de ADR 0009. Prueba de punta
a punta de "Pedir cambios" por el webhook. Todo esto **todavía no se probó en vivo**.

**Punto exacto para retomar (cierre de sesión 2026-09-28).** Árbol limpio en `main`,
frontera de revisión en `dd6ab0a` (review-1b0a5a4777341c90 aprobada y reconocida).
`main` está por delante de `origin/main` (sin push). Base local de trabajo: `prisma`,
creada desde el esquema hasta `0016` y sembrada (`PRUEBA-LOCAL.md` §5); la base
`postgres` conserva los datos de las sesiones 1 y 2, con respaldo
`db/respaldos/prisma-antes-base-nueva-20260928.dump`. En esta sesión, además de lo de
arriba: hallazgo 10 (una pregunta descartada no se reabre, `7e816b6`), `b-0005-b`
(el router reformula referencias, banco real 29 -> 32 aprobados sin empeorar ninguno,
`844a471`) y cada incidente avisa también al administrador por el bot de
administración (`dd6ab0a`, migración `0017`).

Actualización (2026-09-28, más tarde): **#28b cerrada** (backoff 1-2-4-8 minutos, un
aviso agotado deja incidente sin volver a avisar por el canal caído, el token del bot
de administración se toma aunque se configure después; detalle en
`odd/tasks/prisma-orienta.md`). Base `prisma` con la migración `0017` aplicada
(respaldo `db/respaldos/prisma-antes-0017-20260928.dump`); `PRISMA_BOT_TOKEN_ADMIN`
configurado por el usuario. PostgreSQL local (scoop) no es un servicio: tras reiniciar
Windows hay que arrancarlo con `pg_ctl`.

Próximo, en este orden (decisión del usuario: la ronda por Telegram va **al final**,
para probar todo junto):

1. **Administrador alcanzable en modo local:** la base `prisma` no tiene ningún
   `platform_role` 'administrador' y ningún comando lo asigna; `escuchar` no lee el bot
   de administración (`mensaje_admin` sólo se registra por el webhook de `servir`). Sin
   esto, ningún aviso de incidente llega en la ronda local.
2. *(#28c cerrada: la prueba ya no deja `PRISMA_BOT_TOKEN_ADMIN` en el entorno, y el
   incidente de un aviso agotado se escribe en un savepoint: si falla, el lote se
   confirma igual y el fallo se cuenta, se imprime y queda en `ultimo_error`.)*
3. **#29** unificar en `escuchar` (y en `servir`) las rutinas programadas, el despacho
   de la cola y de los avisos al administrador (en `servir` hoy nadie despacha
   `message_outbox` ni `admin_notice`: `reloj.py` sólo encola), con opción para apagar
   las cadencias en pruebas; después **#23** el validador de invariantes
   (`odd/tasks/validador-invariantes.md`: cada 30 minutos los urgentes, una vez por día
   los estructurales, a mano, aviso único por violación al administrador).
4. Escenarios del banco que fallan desde antes de `b-0005-b`: `b-0001`, `b-0001-a`,
   `b-0002-c`, `b-0013`. Menores: T7d (`sembrar`).
5. Recuperación del pack en `main`: saludo, tono e íconos por categoría en los botones
   (pack 06); indicador de "escribiendo" y borrador nativo animado sólo si la respuesta
   tarda, sin demorarla nunca (pack 05).
6. **Tercera ronda por Telegram**, al final: entrega con evidencia y "Pedir cambios"
   (guion de dos circuitos en `odd/tasks/prisma-orienta.md`), más avisos al
   administrador, íconos, indicador de "pensando" y despacho unificado. Antes: aplicar
   las migraciones nuevas a la base `prisma` con respaldo, que el administrador le
   escriba al bot de administración (Telegram descarta a las 24 h los updates no
   leídos) y reiniciar el listener con el código commiteado.

Abierto de esta unidad, sin bloquear: `despachador._fallo` (`message_outbox`) también
reintenta sin espera en horario laboral (`cal.dentro_de_jornada(ahora)` devuelve
`ahora`).

La rama auxiliar `auxiliar/alta-y-google` avanza en su sesión (alta con correo y
Google); `main` cambió mucho desde que se creó, así que le toca traer los cambios de
`main` antes de su próxima rebanada.

Abierto, sin bloquear:

- **Autoridad sobre `cancelada`** (T2b): no se resolvió si una autoridad superior al
  responsable puede cancelar una tarea ajena. `PENDIENTE` de decisión explícita.
- El menú de tarea (T2) todavía no ofrece "Adjuntar evidencia" al aprobador, aunque
  `herramientas.py` ya se lo permite desde T2b — ajuste de UX pendiente.
- `b-0005-b` (banco real, 2026-09-26): Jev resuelve "el plc" a 0,76/0,53 de
  probabilidad/confianza, debajo de `jev.CORTE_CLARA = 0,85`, y Prisma abre una
  aclaración que el escenario no contesta — comportamiento del modelo contra un umbral
  ya codificado, no un defecto de Prisma. `PENDIENTE` de decisión de producto: ajustar
  el umbral o enriquecer el contexto que recibe Jev para referencias informales de una
  sola palabra clave.
- El reintento del despachador puede reordenar las partes de una respuesta partida:
  el orden estrictamente creciente que garantiza `salida.enqueue_outbox` vale para la
  primera pasada, no para una parte reprogramada tras un fallo — límite documentado en
  `odd/tasks/prisma-orienta.md`, no corregido.
- ADR 0007 sigue con dos puntos abiertos en "Pendiente": si una respuesta puede cerrar
  sin ninguna opción, y cómo se ven las opciones en el grupo de gestión.

Después de T5, según [`ROADMAP.md`](ROADMAP.md): **Aportes sobre tareas** (depende de
Prisma orienta), después aprendizaje de apodos y aclaraciones, y la conversación de
bloqueos (mecánica §8, pasos 2 a 7).

El resto del orden de trabajo está en [`ROADMAP.md`](ROADMAP.md).

## Cerrado: Prisma orienta (T1-T4b)

Feature `odd/tasks/prisma-orienta.md`, origen [`ADR 0007`](decisions/0007-prisma-orienta-no-charla.md);
acciones por tarea en
[`architecture/interpretacion-y-confirmacion.md`](architecture/interpretacion-y-confirmacion.md)
§4.6. Construido sobre `main` (commits `c253d27` a `9681973`), cada unidad con su
revisión RDD; detalle completo, decisiones y evidencia de cada corrección en
`odd/tasks/prisma-orienta.md`.

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
  el comprobador `comprobar_pregunta_con_opciones` (activo por defecto: si Prisma
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
`b-0005-b`: Jev da 0,79 a 0,84 a "el plc" (corte 0,85) y Prisma pregunta; es una
pregunta de más, segura. Límites conocidos: "lo del tablero" (`b-0008`) puede elegirse
solo, lo frena la vista previa; ante algo que no existe, Prisma ofrece la tarea
parecida en lugar de decir que no la encuentra. Con los 60 mensajes de los lotes,
Prisma pregunta en uno de cada tres; los lotes son difíciles a propósito y la
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
(`src/prisma/herramientas.py`) crean y quitan con la autoridad decidida —responsable de
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
