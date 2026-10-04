# Estado actual

**Alcance:** Leda es un producto de gestión de proyectos multi-tenant. CoreWork es
su primer cliente, no su definición.

**Última actualización documental:** 2026-10-04, después de la tarea E1-3.

Versiones anteriores (historia, no estado vigente ni instrucción):
[`STATUS-hasta-2026-09-30.md`](historial/STATUS-hasta-2026-09-30.md),
[`STATUS-hasta-2026-10-04.md`](historial/STATUS-hasta-2026-10-04.md) (el flujo C) y
[`STATUS-hasta-M1.md`](historial/STATUS-hasta-M1.md) (con el detalle de lo congelado, la historia de Git y las
revisiones RDD del 2026-10-04), en `historial/`.

## Resumen

La capa de datos y de garantías funciona: aislamiento entre clientes, estado como proyección de eventos,
confirmaciones con vista previa, outbox y auditoría. En ninguna ronda quedó registrado un efecto mal hecho.

La conversación no convergió: flujos A y B (rondas 1 a 4), ADR 0013 y 0014, flujos C1 a C6 y cinco auditorías.
El 2026-10-04 la prueba real volvió a fallar con fallas de la misma clase y el usuario frenó el parcheo: la falla
está en la capa de conversación, escrita a mano y sin un modelo de la conversación
([`research/gestion-del-dialogo-y-arquitecturas-de-agentes.md`](research/gestion-del-dialogo-y-arquitecturas-de-agentes.md)).
Desde entonces el trabajo es **el Motor** ([`../AGENTS.md`](../AGENTS.md), "Nombres que usamos").

**Paso M1 cumplido (2026-10-04).** El usuario aceptó el
[ADR 0017](decisions/0017-por-chat-los-hechos-por-la-web-la-estructura.md) (decisiones 1 a 7: por chat, los
hechos del trabajo; la estructura, en una plataforma web con su propio ADR; el núcleo no se edita) y el diseño
del [ADR 0018](decisions/0018-motor-de-conversacion.md) para la prueba (decisiones 1 a 8: la IA elige jugadas de
una lista cerrada y el código las ejecuta; estado por persona y registro de turnos; circuitos declarados con
fichas y ocho situaciones generales; la prueba chica y sus criterios). El 0018 queda como "propuesta" hasta que
pase la prueba chica. M1 quedó registrado en el documento de la unidad y en la línea "Estado" de cada ADR.

## Punto exacto para retomar (2026-10-04, después de la E1-3)

- **Qué:** el Motor, con la Etapa 1 terminada.
- **Dónde:** rama `feat/motor-de-conversacion`, carpeta `D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion`
  (reglas en [`../AGENTS.md`](../AGENTS.md), "Dónde se trabaja y qué no se hace").
- **Hecho, la tarea E1-3:** `tests/conversaciones/`, con el formato y catorce conversaciones (doce del
  recordatorio y dos para Jev). Dejan 16 decisiones de producto `PENDIENTE` (P1 a P16, en su README).
- **Primer paso, el plan de la Etapa 2** ("Próximo paso"), con las decisiones P1 a P16 del usuario.
- **Acuerdos de trabajo:** chequeo de rumbo escrito antes de cada unidad; consentimiento permanente del usuario
  para los commits de cada unidad y para las revisiones RDD (`tools/rdd_ciclo.py <carpeta> <base>`), que
  comparan la rama con `origin/main`; un cambio en `AGENTS.md` sale de riesgo medio y pide consentimiento, que el
  agente concede solo por ese consentimiento permanente, sin preguntar; esos cambios se juntan; commits sin líneas de atribución; push sólo a `arields85/leda` y cuando lo decida
  el usuario.

## Próximo paso

El avance se registra en `odd/tasks/motor-de-conversacion.md`.

**Etapa 1. Diseño, sin código.** Terminada: ADR 0017 y 0018 (M1), E1-4 y E1-3.

**Etapa 2. Prueba chica y descartable.** Su plan se escribe antes del código. Ya fijado:

- vive fuera de `src/leda` y prueba el recordatorio y lo que la persona contesta (ADR 0018, decisión 5a);
- se aprueba o se frena con los criterios 5b y 5c del ADR 0018 (conversaciones de la E1-3 corridas cinco veces
  contra la IA real, una prueba por Telegram real y el juicio del usuario);
- base nueva `leda_motor` (no existe), migraciones desde la `0030` (`0026` a `0029` son de la rama congelada) y
  tareas ficticias cargadas con `sembrar` (ADR 0017, decisión 5);
- `tools/restriccion_horario.py` tiene que admitir `leda_motor`; el `.env` de la carpeta lo copia el usuario;
  PostgreSQL se levanta a mano (`levantar-postgres.bat`); un solo listener por bot;
- arranca con GPT-6 sol; luna y Jev corren en paralelo (ADR 0018, decisiones 6 y 7).

**Etapa 3. Limpieza y motor de conversación definitivo.** Cortar los enredos con el código viejo, mudar las
pruebas de garantías a archivos limpios, borrar los flujos A y B y, recién entonces, construir el motor de
conversación definitivo. La plataforma web de tareas lleva su propio ADR antes del código (ADR 0017, decisión 5).

**Criterios de paso a `main`.** M1, el usuario acepta los dos ADR: cumplido. M2: el resultado de la prueba chica
registrado en la bitácora, pase o no. M3: motor de conversación construido, flujos viejos borrados, garantías en
verde y prueba real aprobada. Hasta M2 o M3, `main` recibe sólo documentos, por avance rápido y cuando lo decide
el usuario.

## Qué quedó congelado o superado

Lo anterior al Motor no se retoma: los flujos A, B y C1 a C6 (los A y B se borran en la Etapa 3), las tareas del
alta por chat (0-35, 0-36, P-1c, P1-P7, 0-29, 0-17, 0-14 y las demás), el paso de circuitos al flujo C6, R11 y
R12 (no antes de M3, salvo decisión del usuario) y el validador de invariantes (sin decisión del usuario). Los
hallazgos de conversación de la rama de flujo y los C-1 a C-3 de `main` no se arreglan: su situación general
pasa a una conversación de prueba. Destino de cada uno:
[`historial/STATUS-hasta-M1.md`](historial/STATUS-hasta-M1.md), "Qué quedó congelado o superado".

## Decisiones pendientes del usuario

- **El archivo global `~/.claude/CLAUDE.md` (unos 71.000 caracteres).** Claude Code avisa cuando las
  instrucciones que carga al iniciar superan 150.000 caracteres. Desde el 2026-10-04 el proyecto carga
  `AGENTS.md` reducido a lo que sirve, `docs/STATUS.md`, el documento de la unidad, la constitución y la
  mecánica (`nucleo/alta-de-equipo.md` ya no se carga, por el ADR 0017, decisión 7). Medido con
  `LC_ALL=C.UTF-8 wc -m` el 2026-10-04: unos 73.000 caracteres del proyecto y unos 144.000 en total con el
  global. El margen es chico (unos 6.000): `docs/STATUS.md` y el documento de la unidad no deberían crecer. El
  global lo maneja entero gentle-ai (`gentle-ai sync` pisaría una edición a mano): achicarlo lo decide el
  usuario, con esa herramienta.
- **Respaldo de lo no subido.** `main` está subido hasta `e466eb5`. Viven en un solo disco la rama congelada
  `feat/flujo-de-un-mensaje` (92 commits sin subir, 7 con líneas de atribución), los commits de aviso de las
  ramas congeladas, las etiquetas del 2026-10-04 y lo posterior a `e466eb5` en la rama del Motor. Recomendación
  del agente para la rama congelada: no reescribirla (los documentos citan sus hashes) y guardarla con
  `git bundle`.
- **Un bot de Telegram de prueba para la rama del Motor:** hay un solo listener por bot, y uno abierto en la
  carpeta equivocada escribe en la base equivocada.
- **Limpieza de las carpetas viejas** `c4-medicion`, `flujo-c6` y `prueba-0-35` (el listener del usuario puede
  estar corriendo en `prueba-0-35`).

`PENDIENTE` dentro de los ADR, para resolver al llegar: si se avisa que se cargaron tareas (ADR 0017,
decisión 2); cómo se guarda quién destraba un bloqueo y qué pasa si dice que no le corresponde (decisión 3a); el
canal del aviso al administrador de lo que no está en la lista (ADR 0018, decisión 1); las tablas del motor de
conversación (decisión 3, al diseñar la Etapa 2); y cómo llega el tono de cada cliente a la IA. Los de la E1-4
están en las notas de `docs/ROADMAP.md`; los de la E1-3, en `tests/conversaciones/README.md`.

## Estado comprobado

**Código y esquema.** La rama del Motor sólo agregó documentos: su código es el de `main`.

- `row level security` forzado en 34 tablas (recuento del 2026-09-30); aislamiento entre clientes cerrado por
  las migraciones `0003` a `0005` ([`architecture/frontera.md`](architecture/frontera.md#cómo-se-cerró-la-regla-1)).
  `PENDIENTE`: un ensayo de propiedad sobre un clúster enteramente limpio.
- Sin vocabulario de cliente en el esquema: un segundo cliente no exige modificarlo. El estado de tarea es
  proyección de eventos. Migraciones hasta `0025`, cada una con rollback y ensayo de paridad.
- HTTP: `POST /telegram/{slug}`, `GET /tablero/{token}` (sólo lectura) y `GET /salud`; no hay API de lectura.
- La conversación de `main` son los flujos A y B, congelados.
- Para el seguimiento (relevamiento del 2026-10-04): `herramientas.ejecutar` y la vista previa con huella se usan
  sin el código de conversación; hay cinco enredos entre módulos (documento de la unidad); no hay enlace entre
  una respuesta y su recordatorio; `pending_reply` nunca se escribe; no existe la operación de pedir más tiempo;
  los textos de recordatorios y cadencias están fijos en `escalera.py` y `reloj.py`; `sembrar` carga tareas una
  sola vez por espacio y con menos exigencias que el compromiso normal.

**Rama congelada `feat/flujo-de-un-mensaje`:** en `cc732dd` (etiqueta `respaldo-flujos-antes-de-d`) más su commit
de aviso; tiene los flujos C1 a C6, las migraciones `0026` a `0029` y los documentos de sus tareas.

**Git.**

- Repositorio `arields85/leda` (público). `arields85/prisma` queda como respaldo congelado (remoto
  `respaldo-prisma`). Engram usa el proyecto `prisma-pm` (`.engram/config.json`).
- `main` se subió el 2026-10-04 (`aa32a02..6f9b9a3`) y, después de M1, recibió por avance rápido los documentos
  del Motor, por decisión del usuario: `origin/main` está en `e466eb5`. La rama sigue encima con la E1-4.
- Etiquetas: `respaldo-flujos-antes-de-d`, `respaldo-main-antes-de-d` (punto de partida de la rama),
  `respaldo-0-36-en-pausa` (sólo consulta), `pre-renombre-leda` y `respaldo-flujos-antes-de-c2`, `-c5` y `-c6`.
- Ramas: `feat/motor-de-conversacion` (vigente) y `main`; congeladas, `feat/flujo-de-un-mensaje` y
  `auxiliar/alta-y-google` (`c9e7389`, ADR 0010 propuesta); restos sin uso: `feat/flujo-c6` y las copias
  `auxiliar/alta-y-google-*`.

## Baseline de pruebas

| Dónde | Comando | Fecha | Resultado |
|---|---|---|---|
| `main` | `.venv\Scripts\python.exe -m pytest -q` | 2026-09-30 | 2279 passed, 333 deselected |
| `main`, después del renombre | suite completa | 2026-10-02 | 2286 passed |
| Rama congelada, en `24e92ce` | `python -m pytest -q -p no:cacheprovider` | 2026-10-04 | 3997 passed, 333 deselected, 1 warning |
| Punto de partida del Motor (`respaldo-main-antes-de-d`, mismo código que `main`) | `.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` | 2026-10-04 | 2286 passed, 333 deselected, 1 warning in 631.96s |

Los deselected son el banco real (`modelo_real`). La última fila es la línea base de garantías del Motor. Estas
cifras miden el código: **una suite en verde no es evidencia de que la conversación funcione** (`AGENTS.md`,
"Cómo pensamos juntos", punto 12).

## Operación

- Sin producción, trabajo real, Docker ni staging. Telegram real sólo con datos ficticios (cuentas de prueba
  Ariel, Ismael y Marcos, que opera el usuario).
- Bases locales: `leda` (`main`) y `leda_flujo` (rama congelada: migraciones hasta `0029`, IA
  `openai/gpt-6-sol`, CoreWork con `emojis = true`); `leda_motor` no existe. Los roles `leda_*` los comparten
  todas las bases. Respaldos en `db/respaldos/`.
- **Restricción de horario apagada en `leda_flujo`** desde el 2026-10-02; el horario de CoreWork (lunes a
  viernes, 09:00-17:00) vuelve con `tools/restriccion_horario.py prender corework`.
- PostgreSQL local (scoop) no es un servicio: se levanta con `levantar-postgres.bat`. Si se cae con
  `0xC0000142`, un proceso hijo huérfano retiene la memoria compartida: cerrar los procesos `postgres` y volver a
  levantarlo (pasó tres veces; si se repite, buscar la causa).
- El listener lo corre el usuario en su terminal (`python -m leda escuchar corework`); las tareas en segundo
  plano del agente se cortan por tiempo. El 2026-10-04 corría en `prueba-0-35` contra `leda_flujo`.
- Para leer una prueba real: `python tools/leer_conversacion.py [minutos] [desde HH:MM]`, con `PYTHONPATH=src`,
  desde la carpeta de la base. Muestra los botones ofrecidos y cada toque: no sacar conclusiones sin ellos.

## Riesgos prioritarios

1. **El outbox está atado a un transporte:** `message_outbox` tiene `chat_id` y `telegram_message_id` y no tiene
   canal; bloquea toda superficie no conversacional.
2. **Un límite de transporte decide validez de negocio:** `telegram_utf16_units` (`salida.py`) acepta o rechaza
   datos en `ingreso_tareas.py`.
3. **No hay grafo de transiciones de estado:** `actualizar_estado` acepta cualquier destino del enumerado.
4. **`pending_reply` no es operativo:** el seguimiento no puede afirmar silencio. Se construye con el
   seguimiento (ADR 0017, decisión 6).
5. **`confirmar_borrador_tarea` fija el espacio con el valor que recibe:** acotada a `leda_gateway`, pero es el
   patrón que la frontera rechaza.
6. **La conversación no tiene un modelo:** lo resuelve el diseño del ADR 0018, a probar en la Etapa 2.
7. **Lo no subido vive en un solo disco** ("Decisiones pendientes del usuario").
8. **Ningún equipo real usó Leda:** todas las pruebas fueron con datos ficticios y un evaluador que conoce el
   guion.

Contrastar los riesgos 1 a 5 contra el símbolo, no contra números de línea.

## Deudas registradas

Del código de `main`; las de conversación se evalúan en el motor de conversación, no en los flujos congelados.

- **Contexto de la IA:** comparar el contexto amplio con variantes reducidas; requiere ADR antes de operar en
  internet.
- **Producción:** cola de entrada, pool de conexiones, secreto de webhook, observabilidad, respaldo y
  restauración.
- **Alta de un segundo cliente:** el proceso no está definido.
- **Autoridad sobre `cancelada`** (T2b): `PENDIENTE` de decisión.
- **Aviso por cambio de fecha** de dependencias sin disparador (la fecha comprometida es inmutable; su cambio va
  a la plataforma, ADR 0017, decisión 4).
- **Reintento del despachador:** puede reordenar partes de una respuesta partida.
- **`b-0005-b`:** Jev da 0,76/0,53 a "el plc", bajo `jev.CORTE_CLARA = 0,85`; se resuelve con la medición de Jev
  (ADR 0018, decisión 7).
- **ADR 0007:** dos puntos abiertos (respuesta sin opciones; opciones en el grupo de gestión).
- **Configuración:** el resumen "Estado del equipo" va a un grupo de Telegram que no existe (R4b-H7).
- **Tope de contacto por espacio y no por persona** (`docs/capacidades.md`, "Trampas conocidas").
