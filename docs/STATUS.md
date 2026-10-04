# Estado actual

**Alcance:** Leda es un producto de gestión de proyectos multi-tenant. CoreWork es
su primer cliente, no su definición.

**Última actualización documental:** 2026-10-04.

Versiones anteriores de este documento:
[`historial/STATUS-hasta-2026-09-30.md`](historial/STATUS-hasta-2026-09-30.md) (sesiones y unidades
hasta el cierre de la ronda 4) y
[`historial/STATUS-hasta-2026-10-04.md`](historial/STATUS-hasta-2026-10-04.md) (el orden de trabajo del
flujo C, sus puntos de retorno y sus pendientes, hasta el cambio de rumbo del 2026-10-04; literal salvo
el aviso de archivo de su primera línea). Lo que figura en esas copias es historia: no es estado vigente
ni una instrucción.

## Resumen

Leda se define como producto ofrecible a varios clientes, con superficie conversacional,
superficie de lectura y eventual aplicación móvil. La capa de datos y de garantías funciona:
aislamiento entre clientes, estado como proyección de eventos, confirmaciones con vista previa,
outbox y auditoría. En ninguna ronda quedó registrado un efecto mal hecho.

La conversación no convergió. Pasó por las rondas 1 a 4 (flujos A y B), por los ADR 0013 y 0014,
por seis versiones del alta conversada (flujos C1 a C6, en la rama `feat/flujo-de-un-mensaje`) y
por cinco auditorías. El 2026-10-04, la prueba real de la última corrección volvió a fallar con
fallas nuevas de la misma clase. Un análisis adversarial pedido por el usuario concluyó que la
base es correcta y que la falla está en la capa de conversación: está escrita a mano, situación
por situación, sin un modelo de la conversación
([`research/gestion-del-dialogo-y-arquitecturas-de-agentes.md`](research/gestion-del-dialogo-y-arquitecturas-de-agentes.md)).

**El Motor (decisiones del usuario, 2026-10-04).** Así llama el usuario a la línea de trabajo
vigente; qué abarca está definido en [`../AGENTS.md`](../AGENTS.md), "Nombres que usamos". Sus
decisiones:

1. Se deja de corregir la conversación de los flujos A, B y C, que quedan congelados.
2. Se construye un motor chico de conversación dentro de Leda, sin marcos de terceros. Rasa queda
   descartado. Como mecanismo, comparado con los flujos A, B y C, se llama flujo D.
3. Engram se toma sólo como referencia de diseño. El motor de conversación se diseña en tres
   partes: estado exacto, registro completo de la conversación (con los toques de botones) y
   memoria por integrante, que va después y con su propio ADR.
4. Se recorta el alcance: por ahora Leda no crea tareas ni objetivos por chat; hace seguimiento.
   Principio: *por chat, hechos del trabajo; por la web, su estructura.*
5. Las tareas se cargan primero con una importación por archivo que hace el administrador y,
   después, con un formulario en el tablero del cliente.
6. Reglas de conversación para el motor de conversación: los botones son atajos (lo que hace un
   botón también vale escrito) y un tema a la vez, con tres salidas ante un cambio de tema (seguir,
   retomarlo después o cancelarlo). Si lo escrito alcanza a una confirmación que crea o cambia algo
   está `PENDIENTE` en el ADR 0018.
7. Reglas de trabajo: diseño escrito antes del código; cada hallazgo de conversación es primero
   una conversación de prueba; la evidencia son conversaciones reales contra la IA real, corridas
   varias veces; una sola casa para los documentos.

Gobiernan: [`product/que-es-leda.md`](product/que-es-leda.md),
[`architecture/frontera.md`](architecture/frontera.md), [`ROADMAP.md`](ROADMAP.md) y
[`capacidades.md`](capacidades.md). Las reglas de trabajo están en [`../AGENTS.md`](../AGENTS.md); lo
que se probó de cada flujo, en [`product/bitacora-de-flujos.md`](product/bitacora-de-flujos.md).
Documentos superados: [`INDEX.md`](INDEX.md#documentos-superados).

## Punto exacto para retomar (2026-10-04)

- **Qué:** el Motor, la línea de trabajo vigente.
- **Dónde:** rama `feat/motor-de-conversacion`, carpeta
  `D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion`, abierta desde la etiqueta
  `respaldo-main-antes-de-d`. Las sesiones se abren en esa carpeta.
- **Si este archivo se está leyendo en otra carpeta** (por ejemplo `D:\Proyectos\Leda-PM`, que es
  `main`), puede estar atrasado: los documentos vigentes son los de la carpeta nueva. Antes de
  responder hay que leer, de esa carpeta, `AGENTS.md`, `docs/STATUS.md`,
  `odd/tasks/motor-de-conversacion.md` y los tres documentos de `nucleo/`. En `main` no se hace
  ningún commit hasta el paso M1.
- **Carpetas donde nunca se abre una sesión de trabajo:** las congeladas de
  `D:\Proyectos\Leda-PM-worktrees\`: `flujo-de-un-mensaje`, `alta-y-google`, `c4-medicion`,
  `flujo-c6` y `prueba-0-35`. Cada una lleva un aviso de congelamiento al comienzo de su `AGENTS.md`.
- **Siempre una sesión nueva:** una sesión iniciada antes del cambio del 2026-10-04 conserva en su
  contexto las instrucciones anteriores y no se continúa.
- **Lo primero:** escribir con el usuario el ADR 0017 y el ADR 0018 (Etapa 1 de "Próximo paso"),
  punto por punto y sin código.
- **Qué no se hace:** lo que lista [`../AGENTS.md`](../AGENTS.md), "Dónde se trabaja y qué no se
  hace", y lo de "Qué quedó congelado o superado", más abajo.
- **Acuerdos de trabajo vigentes:** chequeo de rumbo escrito antes de cada unidad; consentimiento
  permanente del usuario para los commits de cada unidad y para las revisiones RDD
  (`tools/rdd_ciclo.py <carpeta> <base>`); commits sin líneas de atribución; push sólo a
  `arields85/leda` y cuando lo decida el usuario.
- **Para cuando llegue una prueba real (Etapa 2):** PostgreSQL local se levanta a mano
  (`levantar-postgres.bat`); la base de la rama nueva (`leda_motor`) todavía no existe; el `.env` de
  la carpeta nueva lo copia el usuario; hay un solo listener por bot de Telegram.

## Próximo paso

Orden vigente: el del Motor, el plan que el usuario aprobó el 2026-10-04. El avance se registra en
`odd/tasks/motor-de-conversacion.md`, en la rama nueva.

**Etapa 1. Diseño, sin código.** Dos ADR escritos con el usuario y las primeras conversaciones de
prueba. Lo que cada ADR tiene que resolver está `PENDIENTE` hasta que se acepte: no se da por
decidido ni se actúa sobre ello.

- **ADR 0017, alcance** ("por chat, hechos del trabajo; por la web, su estructura"). Tiene que
  resolver:
  - qué circuitos quedan por chat;
  - qué contesta Leda cuando alguien le pide una tarea nueva por chat;
  - la importación del administrador: quién decide y quién aplica, qué garantías cumple una tarea
    cargada, que se pueda repetir y cómo se audita;
  - el pedido de más tiempo sobre una tarea;
  - la redefinición del congelamiento de funcionalidad nueva y del orden del roadmap;
  - cómo se ajusta `nucleo/` al recorte (esa edición la hace el usuario).
- **ADR 0018, motor de conversación.** El usuario acepta su diseño en el paso M1; su estado queda
  como "propuesta", con la fecha en que el usuario aceptó el diseño para la prueba, hasta que pase
  la prueba de la Etapa 2. Tiene que resolver:
  - el modelo del estado de la conversación y el registro de turnos;
  - qué declara un circuito;
  - las situaciones generales (cambio de tema, corrección, cancelar, escribir en lugar de tocar un
    botón, botón vencido);
  - qué decide la IA y qué decide el código, con la enmienda explícita del punto 11 de `AGENTS.md`
    (la regla del mozo);
  - si una confirmación que crea o cambia algo puede hacerse por escrito;
  - las reglas del arranque limpio: el motor de conversación en un paquete nuevo que sólo alcanza
    una lista permitida de módulos y de tablas, con entrada propia y sin interruptores;
  - la estrategia de pruebas, y los criterios de éxito y de corte de la prueba chica;
  - la IA que se usa (se mantiene GPT-6 sol; falta volver a medir GPT-6 luna) y el aporte de Jev.
- **Conversaciones de prueba** como datos, en `tests/conversaciones/`. Las primeras salen de las
  situaciones generales que mostraron las fallas de la prueba real del 2026-10-04 y los hallazgos
  C-1 a C-3: una salida que se pierde, escribir en lugar de tocar un botón, un botón vencido, un
  aviso que ya no corresponde y una vista previa vencida que se descarta en silencio. Se escriben
  sobre circuitos que queden dentro del alcance (ADR 0017), no sobre el alta por chat, y cruzando
  cada situación general con cada circuito.

**Etapa 2. Prueba chica y descartable.** El circuito más simple, de punta a punta, por Telegram
real, con tareas importadas y una base nueva (`leda_motor`), con los criterios escritos antes. Vive
fuera de `src/leda`.

**Etapa 3. Limpieza y motor de conversación definitivo.** Cortar los enredos entre la capa sólida y
el código de conversación viejo, mudar las pruebas de garantías a archivos limpios, borrar los
flujos A y B y, recién entonces, construir el motor de conversación definitivo y la importación
real.

**Criterios de paso a `main`.** M1: el usuario acepta los dos ADR (sólo documentos). M2: el
resultado de la prueba registrado, pase o no. M3: motor de conversación construido, flujos viejos
borrados, garantías en verde y prueba real aprobada. Hasta M1, `main` no recibe commits y no se
escribe código de conversación; la prueba chica de la Etapa 2 viene después de M1.

**Qué deja registrado M1.** M1 queda registrado en dos lugares: en
`odd/tasks/motor-de-conversacion.md`, con su fecha, y en la línea "Estado" de cada ADR (el 0017,
"aceptada"; el 0018, "propuesta", con la fecha en que el usuario aceptó su diseño para la prueba).
Una sesión nueva comprueba esos dos lugares antes de dar M1 por cumplido.

Las migraciones nuevas empiezan en `0030`: los números `0026` a `0029` son de la rama congelada.

## Qué quedó congelado o superado

Nada de esta lista se retoma: es anterior al Motor. Figura acá para que una sesión nueva sepa qué
pasó con cada pendiente anterior. La historia está en [`historial/STATUS-hasta-2026-10-04.md`](historial/STATUS-hasta-2026-10-04.md)
y, para las tareas de la rama de flujo, en el documento `odd/tasks/circuitos-al-flujo-nuevo.md` de la
etiqueta `respaldo-flujos-antes-de-d` (se lee con `git show`).

| Pendiente anterior | Qué pasó |
|---|---|
| Flujos A, B y C1 a C6 | Congelados. No se corrigen ni se extienden. El código de los flujos A y B se borra en la Etapa 3. |
| Tarea 0-35 (el borrador devuelto como borrador normal) | Construida y revisada en la rama congelada. Su prueba real del 2026-10-04 motivó el cambio de rumbo. No se continúa. |
| Tarea 0-36 (un tema a la vez en el alta, y "Rechazar y cancelar") | Detenida; no se retoma. Su trabajo parcial y sin verificar quedó archivado en la etiqueta `respaldo-0-36-en-pausa`, que se guarda sólo para consulta. Las reglas "un tema a la vez" y "los botones son atajos" pasan al diseño del motor de conversación (ADR 0018). "Rechazar y cancelar" es del alta por chat, fuera del alcance por ahora. |
| P-1c (plantillas del flujo B), 0-17 (estilo con ejemplos), 0-14 (una sola fuente para el tono) y retirar el flujo A del alta | Superados: eran mejoras de flujos congelados. |
| Pasar los circuitos 1 a 10 al flujo C6 | Superado por el Motor. Qué circuitos quedan por chat está `PENDIENTE` en el ADR 0017. |
| P1-P7 (falla del proveedor de la IA) y 0-29 (recordatorio del borrador rechazado) | No se construyen en los flujos congelados. Si hace falta algo equivalente en el Motor (qué pasa cuando la IA no responde, seguir la falta de respuesta) está `PENDIENTE` en los ADR 0017 y 0018. |
| Tope de salida por modelo, elección de la IA desde la plataforma, `llm._limpiar_esquema`, la prueba intermitente del indicador de escritura y la adaptación de `tools/medir_modelos.py` | Pasan a la lista de lo que se trae, se rehace o se descarta de la rama congelada, en `odd/tasks/motor-de-conversacion.md`. |
| Si un aviso a otra persona queda `fallido` al agotar los reintentos | Era del mecanismo de avisos de la rama congelada (ADR 0016). Si el motor de conversación trae ese mecanismo, y con qué regla, está `PENDIENTE` en el ADR 0018. |
| Hallazgos abiertos de la rama de flujo (por ejemplo, la IA que promete lo que no existe o la evidencia mostrada con claves internas) | No se arreglan en la rama congelada. Lo que pasa a las conversaciones de prueba es la situación general que muestran, escrita sobre un circuito que quede dentro del alcance (ADR 0017), no el caso del alta. |
| Hallazgos C-1 a C-3 del código de `main` (una vista previa vencida descartada en silencio, avisos encolados que ya no corresponden y un botón viejo que deja a la persona sin salida) | No se arreglan en los flujos congelados. Sus situaciones generales pasan a ser conversaciones de prueba del motor de conversación, escritas sobre circuitos que queden dentro del alcance (ADR 0017). |
| La moratoria de parches y la prioridad de sacar las plantillas | Reemplazadas por el orden de "Próximo paso". |
| "Escritor, auditoría de otro agente y revisión RDD" como señal de que algo está terminado | Reemplazado por las reglas del punto 12 de "Cómo pensamos juntos" (`AGENTS.md`): no es evidencia de que la conversación funcione. |
| R11 (limpieza del renombre a Leda) y R12 (integración de `auxiliar/alta-y-google` a `main`) | No se retoman antes de M3, salvo decisión del usuario. |
| Validador de invariantes y los demás puntos "en espera" de la copia anterior | No se empiezan sin una decisión del usuario. |

## Decisiones pendientes del usuario

Las que definen el producto se resuelven en los ADR 0017 y 0018 ("Próximo paso"). Aparte:

- **Respaldo o push de lo que no está subido.** Hoy vive en un solo disco: la rama congelada
  `feat/flujo-de-un-mensaje` (92 commits sin subir hasta su etiqueta, 7 con líneas de atribución),
  `main` (20 commits sin subir, ya sin líneas de atribución), los commits del aviso de congelamiento
  de las dos ramas congeladas y las etiquetas nuevas. Recomendación del agente para la rama
  `feat/flujo-de-un-mensaje`: no reescribirla, porque los documentos citan sus hashes, y guardarla
  con `git bundle`. Subir o no lo decide el usuario.
- **Un bot de Telegram de prueba para la rama nueva.** Hay un solo listener por bot, y uno abierto
  en la carpeta equivocada escribe en la base equivocada.
- **Limpieza de las carpetas viejas** `c4-medicion`, `flujo-c6` y `prueba-0-35`. El listener del
  usuario puede estar corriendo en `prueba-0-35`.

## Estado comprobado

**Código y esquema de `main`.** La rama nueva parte de acá.

- Fundación multi-tenant con `row level security` forzado y política de aislamiento
  contra el espacio vigente: 34 tablas (recontadas el 2026-09-30 en `db/esquema.sql`:
  31 en el bucle de la línea 2104 y `absence`, `audit_log` e `incident` aparte, líneas
  2149-2160). Aislamiento entre clientes cerrado por las migraciones `0003` a `0005`
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
- Migraciones hasta `0025` en `db/migrations/`, cada una con rollback y ensayo de paridad en la
  suite. Las `0026` a `0029` existen sólo en la rama congelada.
- La conversación de `main` son los flujos A y B, congelados. Sus circuitos se probaron en vivo por
  Telegram con datos ficticios en la cuarta ronda (2026-09-30): entrega con evidencia y revisión
  (ADR 0009), aprobación que cierra la tarea (ADR 0008), cambios pedidos con motivo visible, alta
  guiada, opciones y menú por tarea (ADR 0007).
- Lo que el seguimiento puede reutilizar y lo que le falta (exploración del 2026-10-04, detalle en la
  sección 6 del relevamiento citado en el Resumen):
  - las operaciones del dominio pasan por `herramientas.ejecutar` y se pueden usar sin el código de
    conversación; la vista previa con huella también;
  - los módulos están enredados en cinco puntos (la entrega crea botones que sólo `gateway` resuelve,
    el despachador usa código de conversación, el ciclo de fondo importa `gateway`, la entrada de un
    mensaje vive dentro de `gateway.py`, y hay imports dentro de funciones hacia `ingreso_tareas`);
  - no hay enlace entre la respuesta de una persona y el recordatorio que la originó;
    `pending_reply` nunca se escribe; no existe una operación para pedir más tiempo; los textos de
    recordatorios y cadencias están fijos en `escalera.py` y `reloj.py`;
  - `python -m leda sembrar` carga tareas sin conversación, pero una sola vez por espacio y con
    menos exigencias que el compromiso normal de una tarea.
- Feature previa "Leda orienta" (T1-T4b) cerrada; ver
  [`../odd/tasks/leda-orienta.md`](../odd/tasks/leda-orienta.md) y su diario en
  [`historial/`](historial/leda-orienta-diario-hasta-2026-09-30.md).

**Rama congelada `feat/flujo-de-un-mensaje`** (congelada en `cc732dd`, etiqueta
`respaldo-flujos-antes-de-d`; el único commit posterior es el aviso de congelamiento de su
`AGENTS.md`). Tiene los flujos C1 a C6 del alta, las migraciones `0026` a `0029`, el ADR 0016 y los
documentos de sus tareas (`odd/tasks/circuitos-al-flujo-nuevo.md` y
`odd/tasks/flujo-de-un-mensaje.md`, que sólo existen ahí). Su última revisión RDD quedó aprobada y
reconocida hasta `28a9bc4` (linaje `review-47c246e4351f127e`).

**Git.**

- El repositorio es `arields85/leda` (público), y ahí van los push. `arields85/prisma` queda
  congelado como respaldo (remoto local `respaldo-prisma`). Engram conserva su proyecto `prisma-pm`,
  fijado en `.engram/config.json`.
- El 2026-10-04 se reescribieron los 19 commits de `main` que no estaban subidos, para quitar las
  líneas de atribución. Cambiaron sólo los mensajes: los árboles son idénticos. La punta anterior,
  `4a07849`, queda en `refs/original/refs/heads/main`. Con el commit de cierre, `main` tiene 20
  commits sin subir.
- Etiquetas del 2026-10-04: `respaldo-flujos-antes-de-d` (la rama de flujo congelada, en
  `cc732dd`), `respaldo-0-36-en-pausa` (archivo del trabajo parcial de la tarea 0-36, sólo para
  consulta: esa tarea se detuvo y no se retoma) y `respaldo-main-antes-de-d` (el commit de cierre
  de `main`, del que sale la rama nueva). Anteriores: `pre-renombre-leda` y
  `respaldo-flujos-antes-de-c2`, `-c5` y `-c6`.
- Ramas:
  - `feat/motor-de-conversacion`: trabajo vigente, el Motor.
  - `main`: sin commits nuevos hasta M1.
  - `feat/flujo-de-un-mensaje`: congelada en su etiqueta; el único commit posterior es el aviso de
    congelamiento de su `AGENTS.md`.
  - `auxiliar/alta-y-google` (alta con correo verificado y Google,
    [`ADR 0010`](decisions/0010-correo-verificado-y-google-en-el-producto.md), propuesta):
    congelada en su punta subida (`c9e7389`); el único commit posterior es el aviso de
    congelamiento de su `AGENTS.md`.
  - Restos congelados, que no se usan: `feat/flujo-c6` y las copias
    `auxiliar/alta-y-google-pre-rebase-0929`, `auxiliar/alta-y-google-pre-unificacion` y
    `auxiliar/alta-y-google-unificada-un-commit`.
- Revisiones RDD de `main` del 2026-10-04: aprobadas y reconocidas hasta el árbol anterior al commit
  de cierre (último linaje, `review-2cd79d43a965879b`), con advertencias no bloqueantes sobre
  `tools/rdd_ciclo.py` y `tools/medir_modelos.py`. El commit de cierre entero excedía el presupuesto
  del revisor (`lens_context_budget_exceeded`), así que se revisó en cuatro tramos sobre una carpeta
  temporal, con el mismo árbol final que el commit: linajes `review-d620b2bb22b7427d`,
  `review-8a63e809807fd809` (riesgo bajo, sin lentes), `review-ee3d1ae8de587d93` y
  `review-02333b9633db361d`, todos aprobados y reconocidos. Observaciones no bloqueantes: los
  enlaces relativos dentro de las copias de `docs/historial/` no resuelven desde esa carpeta, y
  faltaba una corrida de la suite en el punto de partida de la rama (ver "Baseline de pruebas").
- Control de coherencia del 2026-10-04: un auditor independiente simuló el arranque de una sesión
  nueva sobre el commit de cierre, la memoria y Engram. Primera pasada: tres hallazgos altos y seis
  medios, corregidos. Segunda pasada: ningún hallazgo alto.

## Baseline de pruebas

| Dónde | Comando | Fecha | Resultado |
|---|---|---|---|
| `main` | `.venv\Scripts\python.exe -m pytest -q` | 2026-09-30 | 2279 passed, 333 deselected |
| `main`, después del renombre | suite completa | 2026-10-02 | 2286 passed |
| Rama congelada, en `24e92ce` | `python -m pytest -q -p no:cacheprovider` | 2026-10-04 | 3997 passed, 333 deselected, 1 warning |
| Punto de partida del Motor (`respaldo-main-antes-de-d`, mismo código que `main`) | `.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` | 2026-10-04 | 2286 passed, 333 deselected, 1 warning in 631.96s |

Los deselected son los escenarios del banco real (`modelo_real`). Banco real completo (n=1) del
2026-09-30: 108 de 111. La última fila es la línea base de la capa de garantías con la que
arranca la rama del Motor; se corrió desde la carpeta de `main`, que tiene el mismo código.

Estas cifras miden el código, incluida la conversación congelada. **Una suite en verde no es
evidencia de que la conversación funcione** (`AGENTS.md`, "Cómo pensamos juntos", punto 12): la de la
rama congelada pasó entera cada vez y cada prueba real encontró fallas.

## Operación

- Sin producción, sin trabajo real cargado, sin Docker ni staging. Telegram real sólo con datos
  ficticios (cuentas de prueba Ariel, Ismael y Marcos, que opera el usuario).
- Bases en el servidor local: `leda` (código de `main`) y `leda_flujo` (rama congelada: migraciones
  hasta `0029`, IA activa `openai/gpt-6-sol`, CoreWork con `emojis = true`). `leda_motor`, la de la
  rama nueva, todavía no existe. En el servidor sólo quedan los roles `leda_*`, que comparten todas
  las bases. Los respaldos están en `db/respaldos/`.
- **Restricción de horario apagada en `leda_flujo`** desde el 2026-10-02 (horario de CoreWork: todos
  los días, 00:00-23:59). El original (lunes a viernes, 09:00-17:00) se restaura con
  `tools/restriccion_horario.py prender corework`.
- PostgreSQL local (scoop) no es un servicio: después de reiniciar la PC hay que levantarlo con
  `levantar-postgres.bat`. Se cayó con `0xC0000142` el 2026-09-30 y dos veces el 2026-10-02: un
  proceso hijo huérfano retiene la memoria compartida; se cierran los procesos `postgres` y se vuelve
  a levantar. Si se repite, investigar la causa de fondo.
- El listener lo corre el usuario en su propia terminal (`python -m leda escuchar corework`); las
  tareas en segundo plano del agente se cortan por tiempo. El 2026-10-04 corría en la carpeta
  `prueba-0-35` (código de la rama congelada) contra `leda_flujo`; el de `main` está detenido.
- Carpetas de trabajo (`D:\Proyectos\Leda-PM-worktrees\`): `motor-de-conversacion` (vigente, el Motor),
  `flujo-de-un-mensaje` y `alta-y-google` (congeladas), y `c4-medicion`, `flujo-c6` y `prueba-0-35`
  (copias fijas de mediciones y pruebas, a limpiar).
- Para leer una prueba real: `python tools/leer_conversacion.py [minutos] [desde HH:MM]`, con
  `PYTHONPATH=src` desde la carpeta cuya base se quiere leer. Muestra la conversación con los botones
  ofrecidos y la etiqueta de cada toque; no sacar conclusiones sin los botones.
- Banco real de modelos sobre `main` (2026-09-30, n=1, 111 escenarios): mide acople al contrato del
  ruteo, no comprensión. El sistema y el banco quedaron ajustados al comportamiento de
  `deepseek-v4-flash`. Detalle en la copia `historial/STATUS-hasta-2026-10-04.md`.
- Renombre a Leda ([ADR 0015](decisions/0015-renombre-del-producto-a-leda.md)) terminado el
  2026-10-02; su limpieza (R11) no se retoma antes de M3, salvo decisión del usuario.

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
4. **`pending_reply` no es operativo.** La tabla y la escalera existen, pero nada crea ni
   satisface el ciclo de respuesta, de modo que el seguimiento no puede afirmar silencio
   sobre evidencia real. El alcance se recortó al seguimiento; si se adelanta la construcción de
   este ciclo está `PENDIENTE` en el ADR 0017.
5. **`confirmar_borrador_tarea` fija el espacio con el valor que recibe.** Está
   acotada a `leda_gateway` y fuera del alcance de `leda_app`, pero confiar el
   espacio a quien llama es el patrón que la frontera rechaza.
6. **La conversación no tiene un modelo.** El estado de cada conversación se deduce en cada
   mensaje y cada situación es una rama de código. Los flujos A, B y C no lo resolvieron; es lo
   que tiene que resolver el flujo D, el mecanismo del Motor.
7. **Lo que no está subido vive en un solo disco** (ver "Decisiones pendientes del usuario").
8. **Ningún equipo real usó Leda todavía.** Todas las pruebas fueron con datos ficticios y un solo
   evaluador que conoce el guion.

Las referencias de línea de los riesgos 1 a 5 se contrastaron contra el código el 2026-09-30; se
desactualizan con cada cambio, así que conviene contrastar contra el símbolo.

## Deudas registradas

Son deudas del código de `main`. Las que tocan la conversación no se corrigen en los flujos
congelados: se evalúan al diseñar el motor de conversación.

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
  `PENDIENTE` de decisión de producto. El aporte de Jev está `PENDIENTE` de revisión en el
  ADR 0018.
- **ADR 0007**: dos puntos abiertos en "Pendiente" (respuesta sin opciones; opciones en
  el grupo de gestión).
- **Configuración**: el resumen "Estado del equipo" va a un grupo de Telegram que no
  existe ("chat not found", un incidente; R4b-H7).
- **Tope de contacto por espacio y no por persona** (`docs/capacidades.md`, "Trampas conocidas").
