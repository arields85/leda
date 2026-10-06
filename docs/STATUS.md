# Estado actual

**Alcance:** Leda es un producto de gestión de proyectos multi-tenant. CoreWork es
su primer cliente, no su definición.

**Última actualización documental:** 2026-10-06, al registrar la prueba por Telegram real (E2-9) y M2.

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
[ADR 0017](decisions/0017-por-chat-los-hechos-por-la-web-la-estructura.md) (por chat, los hechos del trabajo; la
estructura, en una plataforma web con su propio ADR) y el diseño del
[ADR 0018](decisions/0018-motor-de-conversacion.md) para la prueba (la IA elige jugadas de una lista cerrada y el
código las ejecuta). El 0018 quedó como "propuesta" hasta que pasara la prueba chica.

**Paso M2 cumplido (2026-10-06).** La prueba chica pasó: rondas automáticas 85 de 85 con GPT-6 sol y la
prueba por Telegram real, en la que, según el usuario, Leda no se perdió aun fuera del guion y se siente
conversacional, sin un botón (bitácora de flujos, "Prueba por Telegram real del flujo D"). El usuario
aceptó el ADR 0018 el mismo día.

## Punto exacto para retomar (2026-10-06, M2 cumplido; sigue la Etapa 3)

- **Qué:** el Motor. La Etapa 2 (`odd/tasks/prueba-chica-del-motor.md`) está terminada: E2-1 a E2-9 y M2.
  Sigue la Etapa 3, limpieza y motor de conversación definitivo, que lleva su plan propio, todavía sin
  escribir. El ADR 0018 quedó aceptado (2026-10-06). `main` no recibe nada hasta M3, porque la rama ya mezcla
  documentos con código descartable; la rama está subida como respaldo (usuario, 2026-10-06).
- **Dónde:** rama `feat/motor-de-conversacion`, carpeta `D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion`
  (reglas en [`../AGENTS.md`](../AGENTS.md), "Dónde se trabaja y qué no se hace").
- **Para la Etapa 3:** las observaciones de la prueba real (Leda cuenta de más lo de la cocina; los efectos
  del motor sin `audit_log` ni versión de las reglas) y los `PENDIENTE` de abajo.
- **Antes de nada:** comprobar PostgreSQL (`pg_isready -h localhost -p 5432`); al cerrar la sesión se apaga. Si
  está caído, levantarlo (`levantar-postgres.bat`, o `pg_ctl ... start` como hace ese archivo); con `0xC0000142`,
  cerrar los procesos `postgres` colgados y reintentar. Desde el agente, `pg_ctl start` corre fuera del sandbox:
  dentro, no puede escribir su registro.
- **`leda_motor`** quedó con los datos de la prueba real y el reloj de Leda adelantado al 22/10
  (`python -m prueba_chica.reloj corework volver` lo devuelve). El respaldo de antes de recrearla es
  `db/respaldos/leda_motor-antes-e2-9-20261006.dump`.
- **Acuerdos de trabajo:** chequeo de rumbo escrito antes de cada unidad; consentimiento permanente del usuario
  para los commits de cada unidad y para las revisiones RDD (`tools/rdd_ciclo.py <carpeta> <base>`), por tramos
  desde el último revisado (la rama entera excede al revisor; los informes generados no se revisan); un cambio
  en `AGENTS.md` sale de riesgo medio y el agente concede el consentimiento solo; esos cambios se juntan;
  commits sin líneas de atribución; push sólo a `arields85/leda` y cuando lo decida el usuario.

## Próximo paso

El avance se registra en `odd/tasks/motor-de-conversacion.md`.

**Etapa 1. Diseño, sin código.** Terminada: ADR 0017 y 0018 (M1), E1-4 y E1-3.

**Etapa 2. Prueba chica y descartable.** Plan: `odd/tasks/prueba-chica-del-motor.md`. Terminada: pasó la
prueba por Telegram real (E2-9) y M2 está cumplido (2026-10-06).

**Etapa 3. Limpieza y motor de conversación definitivo.** Cortar los enredos con el código viejo, mudar las
pruebas de garantías a archivos limpios, borrar los flujos A y B y, recién entonces, construir el motor de
conversación definitivo. La plataforma web de tareas lleva su propio ADR antes del código (ADR 0017, decisión 5).

**Criterios de paso a `main`.** M1, el usuario acepta los dos ADR: cumplido. M2: el resultado de la prueba chica
registrado en la bitácora, pase o no: cumplido (2026-10-06, pasó). M3: motor de conversación construido, flujos viejos borrados, garantías en
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

- **El archivo global `~/.claude/CLAUDE.md` (unos 71.000 caracteres).** Claude Code avisa por encima de 150.000
  caracteres al iniciar; el proyecto carga unos 72.000 (`LC_ALL=C.UTF-8 wc -m`, 2026-10-06): `docs/STATUS.md` y
  el documento de la unidad no deberían crecer. El global lo maneja gentle-ai (`gentle-ai sync` pisaría una
  edición a mano): achicarlo lo decide el usuario.
- **Respaldo de lo no subido.** `main` está subido hasta `e466eb5`. Viven en un solo disco la rama congelada
  `feat/flujo-de-un-mensaje` (92 commits sin subir, 7 con líneas de atribución), los commits de aviso de las
  ramas congeladas y las etiquetas del 2026-10-04 (la rama del Motor está subida desde el 2026-10-06). Recomendación
  del agente: guardar la rama congelada con `git bundle`, sin reescribirla (los documentos citan sus hashes).
- **Limpieza de las carpetas viejas** `c4-medicion`, `flujo-c6` y `prueba-0-35` (el listener del usuario puede
  estar corriendo en `prueba-0-35`).

`PENDIENTE` dentro de los ADR y del plan, para resolver al llegar: si se avisa que se cargaron tareas (ADR 0017,
decisión 2); qué pasa si quien destraba dice que no le corresponde (decisión 3a); la tensión entre preguntarle al
referente (3a, paso 4) y "Leda es la PM", al diseñar la persecución completa, que es de la prueba siguiente; qué
hace la persona con una tarea terminada mientras la entrega no se recibe por chat (con el circuito de entrega);
y cómo llega el tono de cada cliente a la IA. Los de la E1-4 están en las notas de `docs/ROADMAP.md`.

## Estado comprobado

**Código y esquema.** La rama del Motor agregó la prueba chica, descartable, en `prueba_chica/` (fuera de
`src/leda`), las migraciones `0030` y `0031` (tablas del motor), las etapas del motor en `src/leda/incidentes.py`
y `leda_motor` en `tools/restriccion_horario.py`; lo demás es el código de `main`.

- `row level security` forzado en 34 tablas (recuento del 2026-09-30) más las de la `0030` y la `0031`;
  aislamiento entre clientes cerrado por las migraciones `0003` a `0005`
  ([`architecture/frontera.md`](architecture/frontera.md#cómo-se-cerró-la-regla-1)). `PENDIENTE`: un ensayo de
  propiedad sobre un clúster enteramente limpio.
- Sin vocabulario de cliente en el esquema. El estado de tarea es proyección de eventos. Migraciones hasta
  `0025` en `main`, más `0030` y `0031` en la rama, cada una con rollback y ensayo de paridad.
- HTTP: `POST /telegram/{slug}`, `GET /tablero/{token}` (sólo lectura) y `GET /salud`; no hay API de lectura.
- La conversación de `main` son los flujos A y B, congelados.
- Para el seguimiento en `main` (relevamiento del 2026-10-04): cinco enredos entre módulos (documento de la
  unidad); no existe la operación de pedir más tiempo; los textos de recordatorios están fijos en `escalera.py`
  y `reloj.py`. La prueba chica lo resuelve por su cuenta.

**Rama congelada `feat/flujo-de-un-mensaje`:** en `cc732dd` (etiqueta `respaldo-flujos-antes-de-d`) más su commit
de aviso; flujos C1 a C6 y migraciones `0026` a `0029`.

**Git.**

- Repositorio `arields85/leda` (público). `arields85/prisma` queda como respaldo congelado (remoto
  `respaldo-prisma`). Engram usa el proyecto `prisma-pm`.
- `origin/main` está en `e466eb5` (documentos del Motor hasta M1, por avance rápido) y no recibe nada hasta M3.
  La rama del Motor está subida a `origin/feat/motor-de-conversacion` como respaldo (2026-10-06).
- Etiquetas: `respaldo-flujos-antes-de-d`, `respaldo-main-antes-de-d` (punto de partida de la rama),
  `respaldo-0-36-en-pausa` (sólo consulta), `pre-renombre-leda` y `respaldo-flujos-antes-de-c2`, `-c5` y `-c6`.
- Ramas: `feat/motor-de-conversacion` (vigente) y `main`; congeladas, `feat/flujo-de-un-mensaje` y
  `auxiliar/alta-y-google` (`c9e7389`, ADR 0010 propuesta); restos sin uso: `feat/flujo-c6` y las copias
  `auxiliar/alta-y-google-*`.

## Baseline de pruebas

| Dónde | Comando | Fecha | Resultado |
|---|---|---|---|
| `main` | `.venv\Scripts\python.exe -m pytest -q` | 2026-09-30 | 2279 passed, 333 deselected |
| Rama congelada, en `24e92ce` | `python -m pytest -q -p no:cacheprovider` | 2026-10-04 | 3997 passed, 333 deselected, 1 warning |
| Punto de partida del Motor (`respaldo-main-antes-de-d`) | `.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` | 2026-10-04 | 2286 passed, 333 deselected, 1 warning in 631.96s |
| Rama del Motor, en la E2-6 | suite completa | 2026-10-05 | 2306 passed, 333 deselected, 1 warning in 780.79s |
| Rama del Motor, `prueba_chica` | `pytest prueba_chica` | 2026-10-06 | 411 passed in 133.45s |

Los deselected son el banco real (`modelo_real`). La tercera fila es la línea base de garantías del Motor. Estas
cifras miden el código: **una suite en verde no es evidencia de que la conversación funcione** (`AGENTS.md`,
"Cómo pensamos juntos", punto 12).

## Operación

- Sin producción, trabajo real, Docker ni staging. Telegram real sólo con datos ficticios (cuentas de prueba
  Ariel, Ismael y Marcos, que opera el usuario).
- Bases locales: `leda` (`main`), `leda_flujo` (rama congelada, hasta `0029`) y `leda_motor` (creada el
  2026-10-05; el `.env` de la carpeta del Motor apunta a ella; respaldo
  `db/respaldos/leda_motor-antes-primer-contacto-20261005.dump`). Los roles `leda_*` los comparten todas las
  bases.
- **Bots del Motor:** dos nuevos, del equipo y de administración, creados por el usuario; sus tokens, en el `.env`
  de la carpeta del Motor (el agente no lo lee). La carpeta tiene su propio `.venv`, con las versiones de `main`.
- **Restricción de horario apagada en `leda_flujo`** desde el 2026-10-02; el horario de CoreWork vuelve con
  `tools/restriccion_horario.py prender corework`.
- PostgreSQL local (scoop) se levanta con `levantar-postgres.bat`. Si se cae con `0xC0000142`, un proceso
  huérfano retiene la memoria compartida: cerrar los `postgres` y volver a levantarlo (pasó tres veces).
- El listener lo corre el usuario en su terminal; las tareas en segundo plano del agente se cortan por tiempo. El
  del Motor es `python -m prueba_chica.escuchar corework`, con el `.venv` de la carpeta; el reloj de Leda, `python
  -m prueba_chica.reloj corework adelantar|estado|volver`; el registro de turnos, `python -m prueba_chica.leer
  corework`. Para los flujos viejos, `tools/leer_conversacion.py` (`PYTHONPATH=src`).

## Riesgos prioritarios

1. **El outbox está atado a un transporte:** `message_outbox` tiene `chat_id` y `telegram_message_id` y no tiene
   canal; bloquea toda superficie no conversacional.
2. **Un límite de transporte decide validez de negocio:** `telegram_utf16_units` (`salida.py`) acepta o rechaza
   datos en `ingreso_tareas.py`.
3. **No hay grafo de transiciones de estado:** `actualizar_estado` acepta cualquier destino del enumerado.
4. **`pending_reply` no es operativo en `main`:** el seguimiento no puede afirmar silencio. La prueba chica lo
   escribe; en `src/leda` se construye con el seguimiento (ADR 0017, decisión 6).
5. **`confirmar_borrador_tarea` fija el espacio con el valor que recibe:** acotada a `leda_gateway`, pero es el
   patrón que la frontera rechaza.
6. **La conversación no tiene un modelo en `main`:** el diseño del ADR 0018 pasó la prueba chica (rondas y
   Telegram real), pero vive en `prueba_chica/`, que es descartable; el motor definitivo es la Etapa 3.
7. **Lo no subido vive en un solo disco:** la rama congelada y las etiquetas ("Decisiones pendientes del
   usuario"); la rama del Motor ya está subida.
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
- **ADR 0007:** dos puntos abiertos (respuesta sin opciones; opciones en el grupo de gestión).
- **Configuración:** el resumen "Estado del equipo" va a un grupo de Telegram que no existe (R4b-H7).
- **Tope de contacto por espacio y no por persona** (`docs/capacidades.md`, "Trampas conocidas").

`b-0005-b` (Jev con "el plc") quedó cerrada el 2026-10-06 por la medición de Jev (ADR 0018, decisión 7).
