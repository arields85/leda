# Estado actual

**Alcance:** Leda es un producto de gestión de proyectos multi-tenant. CoreWork es
su primer cliente, no su definición.

**Última actualización documental:** 2026-10-15, a la tarde, cierre de la sesión de decisiones, J7 hasta J7-5b y diseño (ver "Punto exacto para retomar").

Versiones anteriores (historia, no estado vigente ni instrucción):
[`STATUS-hasta-2026-09-30.md`](historial/STATUS-hasta-2026-09-30.md),
[`STATUS-hasta-2026-10-04.md`](historial/STATUS-hasta-2026-10-04.md) (el flujo C),
[`STATUS-hasta-M1.md`](historial/STATUS-hasta-M1.md) y [`STATUS-hasta-M3.md`](historial/STATUS-hasta-M3.md),
en `historial/`.

## Resumen

La capa de datos y de garantías funciona: aislamiento entre clientes, estado como proyección de eventos,
confirmaciones con vista previa, outbox y auditoría. En ninguna ronda quedó registrado un efecto mal hecho.

La conversación escrita a mano no convergió: flujos A, B y C1 a C6, cinco auditorías. El 2026-10-04 el usuario
frenó el parcheo, y desde entonces el trabajo es **el Motor** ([`../AGENTS.md`](../AGENTS.md), "Nombres que
usamos"): la IA elige jugadas de una lista cerrada y el código las ejecuta (ADR 0017 y 0018, aceptados).

- **M1 (2026-10-04):** el usuario aceptó los ADR 0017 y 0018.
- **M2 (2026-10-06):** la prueba chica pasó: rondas automáticas 85 de 85 y Telegram real.
- **M3 (2026-10-07):** el motor definitivo está construido (`src/leda/motor/`), los flujos A y B borrados, las
  garantías en verde, y el usuario aprobó la prueba por Telegram real ("si, aprobado. va muy bien"). Detalle en
  la bitácora de flujos.

Hoy Leda conversa con `python -m leda escuchar corework`, con GPT-6 sol por la suscripción de ChatGPT del
usuario (proveedor `chatgpt`; uso personal, decisión del usuario). La regresión de las 20 conversaciones de
prueba dio 100 de 100 en las 01 a 20 (2026-10-07, con el margen para corregir); con la regla del motivo de
un atraso, garantías y comprensión 5 de 5 en las 01 a 20 y la 24 (2026-10-08). La entrega y la revisión por
chat (Fase C) pasan las garantías con la IA real y la prueba del usuario por Telegram (bitácora).

## Punto exacto para retomar (2026-10-15, a la tarde)

**Dónde:** rama `feat/motor-de-conversacion`, carpeta `D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion`.
La unidad en curso es [`../odd/tasks/plataforma-jerarquias.md`](../odd/tasks/plataforma-jerarquias.md): el
[ADR 0023](decisions/0023-quien-crea-en-la-plataforma.md) en porciones J1 a J7, y la Mini App (MA), en el
[ADR 0024](decisions/0024-entrar-con-telegram.md).

**Hecho:** J1 a J4 y la Mini App, cerradas. **La noche del 2026-10-15, sola** (todo con RDD aprobada, subido;
detalle en el documento de la unidad): la MA-7 ("Cerrar sesión" en la compu), la ronda real de la 50 y la 55
(10 de 10), las deudas de la MA, lo claro de "Lenguaje", el ADR 0025 (propuesta), la base del cambio de fecha
(J5 S2), el ensayo de propiedad sobre un clúster limpio y la T8, la parte 1 del grafo de transiciones (más su
arreglo para varias filas), el candado de la sesión de ChatGPT y los planes de la J5 y la J6. `leda_motor` en la
`0084`, la `0085` sin aplicar hasta su RDD (último respaldo `db/respaldos/leda_motor-antes-0084-20261015.dump`).

**Antes de nada:** comprobar PostgreSQL (`pg_isready -h localhost -p 5432`). Si no responde aunque `pg_ctl
status` diga que corre (pasó el 2026-10-14: error de memoria compartida), cerrar con `taskkill /F` TODOS los
`postgres.exe` y arrancar con `pg_ctl ... start -l` a un registro nuevo (el viejo puede quedar tomado), fuera
del sandbox. Antes de una ronda con la IA real, comprobar que no corra el escuchador del usuario (`tasklist`): si
corre, la ronda queda pendiente; el escuchador no se apaga, es del usuario.

**Decidido con el usuario (2026-10-15, de mañana):** todo "Para decidir al despertar" del documento de la unidad:
la palabra que reemplaza a "trabada" (hecho y probado con la IA real: en la 55, de 25 a 0), los 12 puntos de la J5
(ADR 0025 **aceptado**), los 9 de la J6, las 10 preguntas de la J7, el mensaje cuando la IA falla (hace falta
construir la respuesta pendiente antes de decirlo), «Mi espacio» sin el botón del menú, la sesión de
administración (12 h sin uso, configurable), el grafo (cancelar, reabrir, deshacer "la empecé" siempre) y los
hallazgos de la ronda. Cada respuesta está escrita en su punto, marcada DECIDIDO o CONTESTADO.

**Dónde quedó (cierre del 2026-10-15, tarde):** J7-0 a J7-5 y J7-5b hechas (equipo que cuadra, el pack sólo arma
un equipo vacío, ver el equipo, áreas, alta con enlace, nombre por espacio). **2026-10-15, noche:** RDD de
`9d871545` aprobada en tres pedazos; alta duplicada corregida (`a71d2623`, también en áreas; RDD aprobada);
`0085` aplicada a `leda_motor` (respaldo `db/respaldos/leda_motor-antes-0085-20261015.dump`, ensayo limpio); web
reiniciada. **Sigue:** J7-6 en adelante. **Diseño:** con impeccable (siempre por su proceso, nunca a mano):
`PRODUCT.md`, `DESIGN.md`, la dirección en `.impeccable/surfaces/web-src-app-tsx.md` y las referencias
`.impeccable/mocks/decision/r7-profundidad*.html`; la barra pegada al borde ya está en las dos y en `DESIGN.md`
(`e793e57e`); el usuario sigue ajustando con `/impeccable live` (el script de `live` se inyecta en las muestras:
nunca commitearlo).

**Lo que sigue, a construir, en este orden** (usuario, 2026-10-15: "todo lo que requiera armar equipo,
configurar equipo… quisiera darle prioridad; las otras son mejoras"; "ese es el orden correcto"): 1. **la J7**, armar
el equipo desde la web (plan en porciones primero); 2. **configurar el equipo desde la web** (horario, feriados,
cadencias, informe, evidencia por área, límites, la sesión de administración y exportar como respaldo: la
"segunda versión" del ADR 0022; sus decisiones de a una antes del código); 3. **ausencias y suplente de
Dirección**; 4. la J5; 5. la J6; 6. las mejoras chicas («Mi espacio», cancelar y reabrir, los hallazgos, la
respuesta pendiente cuando falla la IA).
Falta que el usuario mire en la compu la MA-7 y "te la pidió".

**Sin el usuario, si queda tiempo:** las advertencias de RDD anotadas en cada entrada del documento de la unidad
(ninguna bloquea), y el grafo no se vuelve a tocar sin mirarlo con el usuario (dos arreglos seguidos).

En cada porción: explorar lo que existe ("De qué se parte"), conversación de prueba antes que el código cuando
toca el chat, escritor delegado con la regla de LF, prueba primero, RDD por commit (`tools/rdd_ciclo.py` en un
worktree temporal), la ronda real de las conversaciones afectadas, y al cerrar cada tarea el documento de la
unidad, este punto, Engram y la memoria. Para el celular hacen falta la web y el túnel: sólo cuando el usuario
esté; el escuchador lo reinicia él.

**Acuerdos** (2026-10-14): las decisiones de cada porción se traen al principio, de a una y en texto; los avisos
cuentan lo que vale ahora, no la historia; un cambio de plazo trae el informe de "en qué afecta" antes de
decidir; pedir a Leda que abra la app no lleva botón (dice que toque «Mi espacio»), y la bienvenida sí.

**Para probar en el celular:** el agente levanta la web (`uvicorn leda.entrada:app ... --no-access-log`; sin
`--no-access-log` el registro mostraría el pase de la compu) y el túnel en segundo plano, y pone la dirección
nueva en `LEDA_BASE_URL` del `.env`. Si la Mini App dice "No se pudo entrar" con una apertura nueva, reiniciar la
web (pasó una vez el 2026-10-14, causa no encontrada). Lo que sigue a la plataforma, en orden: `ROADMAP.md`.

**La IA real:** autorizada de forma permanente para todas las pruebas (usuario, 2026-10-14), sin preguntar
antes de cada ronda ni de una repetición. Se sigue gastando poco: una ronda por vez y sólo los casos afectados.
Al primer error de cupo se para todo lo de la IA real y queda pendiente hasta que el usuario cambie de cuenta;
mientras tanto sigue lo demás. La lanza el coordinador
en segundo plano, con la salida a un archivo que guarda `salida=$?` del corredor (probado el 2026-10-09: un
proceso de 90 minutos sobrevivió y avisó al terminar); nunca un escritor. El corredor se corta solo al primer error de cupo (sale con 4). Si se
corta, el usuario cambia de cuenta a mano (`leda chatgpt salir` y `login`); decidió no rotar cuentas
automáticamente. Una ronda completa de las 29 cuesta unas 1.500 a 1.800 llamadas.

**Comandos de la prueba por Telegram** (cada uno entero en un renglón, desde la carpeta del Motor; el
guion es `docs/product/guion-telegram-fase-c-parte-1.md`):
- Terminal 1: `$env:LEDA_BASE_URL = "http://localhost:8000"` y después
  `.venv\Scripts\python.exe -m leda escuchar corework`.
- Terminal 2, la página: `.venv\Scripts\python.exe -m uvicorn leda.entrada:app --host 127.0.0.1 --port 8000 --no-access-log`
  (no `servir`, que arranca otro ciclo de Leda).
- Terminal 3, el reloj: `.venv\Scripts\python.exe -m leda.motor.reloj corework adelantar|estado|volver`;
  esperar 2 minutos reales entre saltos. Registro de turnos: `.venv\Scripts\python.exe -m leda.motor.leer corework --completo`.
- **Ojo:** nunca el escuchador y una ronda del corredor a la vez, ni una ronda real mientras se edita `src/`.

**`leda_motor`:** recreada el 2026-10-12 a la madrugada para la prueba por Telegram (respaldo previo
`db/respaldos/leda_motor-antes-recrear-prueba-telegram-20261012.dump`) y, después de la prueba, llevada
hasta la `0064`: respaldo `db/respaldos/leda_motor-antes-0057-a-0064-20261012.dump` (`pg_restore --list`
sin error), las ocho migraciones ensayadas en una copia descartable restaurada del respaldo y aplicadas
con `psql -v ON_ERROR_STOP=1 -f` como `postgres` (`host=localhost user=postgres dbname=leda_motor`),
sin error. Quedó con lo conversado en la prueba (PLC y dashboard terminados; comunicaciones trabada por
Mariano; integrar, de Marcos) y el reloj de Leda adelantado al miércoles 14/10; para volver a probar
desde cero, recrearla con los pasos de la D6. El 2026-10-13 a la madrugada se llevó a la `0066` (respaldo
`db/respaldos/leda_motor-antes-0065-0066-20261013.dump`, ensayo en una copia descartable). El usuario autorizó ponerla al día o recrearla cuando haga
falta, con respaldo previo; nunca `leda` ni `leda_flujo`.

**Acuerdos de trabajo** (detalle en la memoria del agente):
- **Autonomía:** el agente encadena el trabajo técnico y sólo para ante decisiones de producto, que explica
  con el hilo completo de mensajes, sin cortar, y comandos de un renglón para copiar.
- **Commits:** los de cada unidad, sin líneas de atribución; los escritores delegados no reescriben commits.
  La rama se sube a `arields85/leda` (autorizado); `main` lo decide el usuario.
- **RDD:** consentimiento permanente; se revisa por tramos con `tools/rdd_ciclo.py <carpeta> <base>` en una
  carpeta temporal. Los informes generados y los commits sólo de documentos no se revisan; el aviso de
  "revisar la rama entera" y el de cambios de un escritor que sigue trabajando no se corren.

## Próximo paso

**Etapa 1** (diseño) y **Etapa 2** (prueba chica): terminadas, M1 y M2.

**Etapa 3** (limpieza y motor definitivo): terminada, M3 (2026-10-07). Plan y evidencia en
`odd/tasks/motor-definitivo.md`. Sus cierres están hechos (2026-10-07): las palabras de todos los días, el
formato de los mensajes (aprobado por el usuario), `prueba_chica/` borrada y `main` con el motor.

**Después:** la Fase C y sus correcciones, cerradas (2026-10-12 y 13), y la plataforma web (ADR 0022 y 0023).
El orden de lo que sigue (la plataforma por jerarquía, Leda con un equipo real, la API de lectura y el dashboard,
y lo anotado para más adelante), acordado con el usuario el 2026-10-13, está en `ROADMAP.md`, "Lo que sigue a
la plataforma". No hay equipo real hasta que el usuario lo diga.

## Qué quedó congelado o superado

Lo anterior al Motor no se retoma: los flujos A, B y C1 a C6 (A y B ya borrados de la rama), las tareas del alta
por chat (0-35, 0-36, P-1c, P1-P7, 0-29, 0-17, 0-14 y las demás), el paso de circuitos al flujo C6, R11, R12 y el
validador de invariantes. Destino de cada uno:
[`historial/STATUS-hasta-M1.md`](historial/STATUS-hasta-M1.md), "Qué quedó congelado o superado".

## Decisiones pendientes del usuario

- **Las que deje el agente trabajando solo** (desde la noche del 2026-10-13): en
  `../odd/tasks/plataforma-jerarquias.md`, sección "Para decidir al despertar".
- **Copiar el respaldo a la nube o a otro disco.** El `git bundle` del repositorio entero, con la rama congelada
  `feat/flujo-de-un-mensaje` y todas las etiquetas, está en
  `D:\Proyectos\Leda-PM-respaldos\leda-repositorio-completo-20261007.bundle` (2026-10-07, verificado), en el
  mismo disco.
- **El archivo global `~/.claude/CLAUDE.md`** (unos 71.300 caracteres, de gentle-ai) más lo que carga el
  proyecto suman unos 138.700 de 150.000 (`LC_ALL=C.UTF-8 wc -m`, 2026-10-09, con el documento del Motor
  reducido).
- **`PENDIENTE` dentro de los ADR y del plan:**
  - qué pasa si quien destraba dice que no le corresponde (3a);
  - preguntarle al referente sin dejar de ser Leda la PM;
  - cómo llega el tono de cada cliente a la IA;
  - si cancelar un borrador tiene que dejar auditoría.

## Estado comprobado

**Código y esquema** (rama del Motor):
- **El motor de conversación** es `src/leda/motor/`, con 3 capas, el escuchador, `recibir.py` (compartido con
  el webhook) y `chatgpt.py`.
- **La entrada HTTP** es `src/leda/entrada.py`: `POST /telegram/{slug}`, con un secreto propio de cada bot,
  `GET /tablero/{token}` y `GET /salud`.
- **Borrado:** los flujos A y B (`gateway`, `ingreso_tareas`, `agente`, `contexto`, `respuesta_unica`,
  `deteccion_pregunta`, `jev` y `local`) y la escalera, el reloj y el ciclo viejos.
- **La auditoría vuelve a la cocina:** cada `herramientas.ejecutar` y cada efecto propio del motor deja su fila
  en `audit_log`, con `pack_hash` y `nucleo_hash`.
- **Migraciones:** hasta `0025` y de `0030` a `0056` en `main`; de `0057` a `0085` (la plataforma, el acceso por chat, el cambio de fecha, el grafo y el equipo) en la rama. La `0032` borra las tablas del alta.
  Cada una tiene su rollback y su ensayo de paridad.
- **Seguridad de la base:** `row level security` forzado en todas las tablas con alcance de espacio.
  Ensayo de propiedad sobre un clúster limpio, 2026-10-15 (`tools/ensayo_propiedad.py`): propietarios y RLS
  bien; una base migrada desde el principio difiere en 3 privilegios de roles sin acceso de la app (T8 de
  `odd/tasks/aislamiento-entre-clientes.md`).
- **Las pruebas de garantías** están en `tests/garantias/`, con fronteras que impiden importar código viejo. Las
  del motor, en `tests/motor/`. El corredor y las 20 conversaciones de prueba, en `tests/conversaciones/`
  (`python -m tests.conversaciones.correr --ia …`).
- **La salida con formato:** la IA escribe `**negrita**`, párrafos y "• "; el outbox guarda ese texto y el
  despachador lo manda como texto plano con entidades de Telegram (`salida.formatear`), sin `parse_mode`.
- **Lo que lee la IA al redactar:** los nombres de los datos se traducen a palabras de todos los días
  (`hechos.para_redactar`); adentro no cambian.
- **`prueba_chica/`** se borró el 2026-10-07 (`c43e3e5`); el lector de turnos es `leda.motor.leer`.

**Git:**
- Repositorio `arields85/leda` (público). `origin/main` está en `80d6945` (2026-10-12): la rama del Motor
  llegó por avance rápido el 2026-10-07 (221 commits) y el 2026-10-12 (396 commits, con la Fase C),
  sin atribuciones ni secretos.
- La rama del Motor se sube al cerrar cada tramo.
- Etiquetas: `respaldo-flujos-antes-de-d`, `respaldo-main-antes-de-d`, `respaldo-0-36-en-pausa`,
  `archivo-c4-medicion`, `archivo-flujo-c6`, `archivo-prueba-0-35` y `respaldo-antes-de-partir-limpieza`
  (todas locales salvo las del 2026-10-04).
- Ramas congeladas: `feat/flujo-de-un-mensaje` y `auxiliar/alta-y-google`, con sus carpetas en
  `Leda-PM-worktrees`. `feat/plataforma` ya está en la del Motor; su carpeta y su rama local se borraron el
  2026-10-12 (queda en `origin`). Las carpetas `c4-medicion`, `flujo-c6` y `prueba-0-35` se borraron el 2026-10-07; sus
  `.env`, sin leer, quedaron en `Leda-PM-worktrees\_archivo-env-de-carpetas-borradas`.

## Línea base de pruebas

| Dónde | Comando | Fecha | Resultado |
|---|---|---|---|
| `main` | `.venv\Scripts\python.exe -m pytest -q` | 2026-09-30 | 2279 passed, 333 deselected |
| Punto de partida del Motor (`respaldo-main-antes-de-d`) | suite completa | 2026-10-04 | 2286 passed, 333 deselected |
| Rama del Motor, con la porción 1 de C-3 y el margen | suite completa | 2026-10-07 | 1317 passed |
| Rama del Motor, con el motivo de un atraso | `pytest tests/motor tests/conversaciones` | 2026-10-08 | 707 passed |
| Rama del Motor, con la C-3 hasta la porción 4 y la `0037` | suite completa | 2026-10-08 | 1524 passed |
| Rama del Motor, con la C-3d hasta la D8 (`792392b`) | suite completa | 2026-10-08 | 1659 passed |
| Rama del Motor, ídem | `pytest tests/garantias` | 2026-10-08 | 326 passed |
| Rama del Motor, ídem | `correr --ia guionada --veces 1` (en seco) | 2026-10-08 | 29 de 29 bien |
| Rama del Motor, con la C-5, la C-6 y la C-7 (`e082010`) | suite completa | 2026-10-09 | 1857 passed |
| Rama del Motor, con las decisiones 24 a 55 y la porción 5 (`c06fa6d`) | `pytest tests/motor tests/garantias tests/conversaciones tests/test_administrador_plataforma.py` | 2026-10-10 | 1740 passed |
| Rama del Motor, ídem | `correr --ia guionada --veces 1` (en seco) | 2026-10-10 | 45 de 45 bien |
| Rama del Motor, con los apodos (dos porciones), el cupo y las 48 y 49 (`e4d4f3a`) | `pytest -q` (suite completa) | 2026-10-11 | 2350 passed (30 min) |
| Rama del Motor, ídem (`65086af`) | `correr --ia guionada --veces 1` (en seco) | 2026-10-11 | 47 de 47 bien |
| Rama del Motor, con las decisiones 65 a 73 y el orden de las jugadas (`f0d18e6`) | `pytest -q tests/motor` | 2026-10-11 | 1302 passed |
| Rama del Motor, ídem | `pytest -q tests/garantias` | 2026-10-11 | 475 passed |
| Rama del Motor, ídem | `pytest -q tests/conversaciones` | 2026-10-11 | 194 passed |
| Rama del Motor, ídem | `correr --ia guionada --veces 1` (en seco) | 2026-10-11 | 48 de 48 bien |
| Rama del Motor, con la plataforma junta y `leda_motor` en la `0064` (`7f752d5`) | `pytest -q tests/garantias tests/motor` | 2026-10-12 | 2026 passed (37 min) |
| Rama del Motor, ídem | `npm test` en `web/` | 2026-10-12 | 57 passed |
| Rama del Motor, con la J2 entera (`eaf84ed4`) | `LEDA_BASE_URL= LEDA_GEMINI_API_KEY= pytest -q` (suite completa) | 2026-10-13 | 3286 passed (31 min) |

**Conversaciones con la IA real** (bitácora de flujos):
- La ronda 3 de la prueba chica dio 85 de 85.
- La regresión del motor definitivo con sol por OpenRouter dio 89 de 90.
- Con sol por la suscripción dio 90 de 90; con las palabras de todos los días, 94 de 95 y 95 de 95; con el
  formato de los mensajes, 100 de 100 (20 conversaciones); con el margen para corregir, 100 de 100 en las 01 a 20
  y la corrección de la 25 bien 5 de 5. El mensaje sin puntuación del usuario se lee mal 5 de 5.
- Fase C, 2026-10-11: las siete conversaciones tocadas por las decisiones 66 a 73, garantías 35 de 35;
  la 35 con el orden de las jugadas, garantías y comprensión 5 de 5; con la forma que da la cocina,
  las mismas siete: garantías 39 de 40 (la falla era del corredor, arreglado) y formato 87 → 15.

Las cifras de pruebas miden el código: **una suite en verde no es evidencia de que la conversación funcione**
(`AGENTS.md`, punto 12).

## Operación

- **Entorno:** sin producción, trabajo real, Docker ni staging. Telegram real sólo con datos ficticios (cuentas
  de prueba Ariel, Ismael y Marcos, que opera el usuario).
- **Bases locales:**
  - `leda`, de `main`.
  - `leda_flujo`, de la rama congelada, con la restricción de horario apagada desde el 2026-10-02.
  - `leda_motor`, a la que apunta el `.env` de la carpeta del Motor.
  - Los roles `leda_*` los comparten todas.
- **Bots del Motor:** el del equipo y el de administración. Sus tokens están en el `.env` de la carpeta del
  Motor, que el agente no lee. La carpeta tiene su propio `.venv`.
- **La sesión de ChatGPT del usuario** está en `~/.leda/chatgpt.json`, fuera del repositorio, y se renueva sola
  (`leda chatgpt estado`).
- **En OpenRouter** quedan unos USD 2 de crédito. Con la suscripción no hace falta para sol.
- **El escuchador** lo corre el usuario en su terminal. Un comando en segundo plano del agente no se corta por
  tiempo (probado el 2026-10-09 con 90 minutos), pero el escuchador sigue siendo del usuario.

## Riesgos prioritarios

1. **El outbox está atado a un transporte:** `message_outbox` tiene `chat_id` y `telegram_message_id` y no tiene
   canal; bloquea toda superficie no conversacional.
2. **Un límite de transporte decide validez de negocio:** `telegram_utf16_units` (`salida.py`).
3. **El grafo de transiciones de estado, en parte:** desde la `0079` la base exige lo de la mecánica §3 (el
   evento sale del estado vigente, de `cancelada` no se sale, de `bloqueada` se vuelve al estado previo o se
   cancela); los demás saltos de `actualizar_estado` esperan las decisiones del usuario (quién cancela, objetivos).
4. **`confirmar_borrador_tarea` fija el espacio con el valor que recibe:** acotada a `leda_gateway`, pero es el
   patrón que la frontera rechaza.
5. **La IA por la suscripción del usuario** sirve sólo para uso personal. Depende de un servicio no oficial de
   OpenAI, que puede cambiar sin aviso. En la etapa comercial, cada cliente pone su proveedor.
6. **Ningún equipo real usó Leda:** todas las pruebas fueron con datos ficticios y un evaluador que conoce el
   guion.

Contrastar los riesgos 1 a 4 contra el símbolo, no contra números de línea.

## Deudas registradas

- **Auditoría del lenguaje que sale del código** — **hecha en dos porciones** (2026-10-15: lo claro, y
  "trabada"; tarea "Lenguaje" en `odd/tasks/plataforma-jerarquias.md`, con las dos rondas con la IA real). Queda
  poco y técnico: borrar `NO_EFFECT_STATUS` (retira una prueba de garantías) y textos que la persona no ve hoy
  (vistas previas de `herramientas.py`, `cli.py` del operador). La prueba de guarda impide que vuelvan nombres
  internos a lo que lee la IA. (Pedido del usuario, 2026-10-13; para antes de la próxima
  prueba real grande): que Leda hable siempre natural y cálida. Dos frentes: lo que la cocina le pasa a la IA
  (nombres de datos que escapen a `hechos.para_redactar`, estados internos, fechas técnicas, códigos de
  motivo: lo que la IA pueda copiar tal cual) y los textos que el código manda directo sin la IA (botones,
  mensajes fijos, avisos de error, textos de la web). Antecedente: "Las palabras de todos los días" en la
  bitácora (2026-10-07: "previsión" 85 → 0). Un explorador arma la lista con ejemplos y arreglo propuesto, y
  se pule con el usuario.
- **Producción:**
  - Faltan cola de entrada, pool de conexiones, observabilidad, respaldo y restauración.
  - El webhook atiende un mensaje a la vez, bajo un candado global, y el candado de cada mensaje sigue tomado
    mientras responde la IA (revisión de la E3-7).
- **Sesión de ChatGPT:** el candado entre procesos para renovarla, hecho (`5ad5fd2e`, 2026-10-15).
- **Honestidad en casos de borde** (revisión de la E3-6):
  - un aviso cuya hora ya pasó se anuncia con esa hora (la prueba de M3 lo mostró una vez);
  - el aviso al administrador;
  - los códigos de `hechos`.
- **Una pregunta "para después" vuelve días más tarde en medio de otro tema** (prueba de M3).
- **Vencimiento en fin de semana:** la escalera alrededor de un fin de semana está probada
  (`tests/motor/test_escalera_fin_de_semana.py`, 2026-10-09: un viernes escala el miércoles, el
  aviso previo cruza fines de semana y feriados, la comprimida no saltea pasos). Un vencimiento
  sábado o domingo: la plataforma no lo dejará cargar (decisión 56, 2026-10-10); el que entre por
  otro lado cuenta como si venciera el viernes anterior.
- **Contexto de la IA:** comparar el contexto amplio con variantes reducidas; requiere ADR antes de operar en
  internet.
- **Alta de un segundo cliente:** el proceso no está definido.
- **Autoridad sobre `cancelada`** (T2b): `PENDIENTE` de decisión.
- **Reintento del despachador:** puede reordenar partes de una respuesta partida.
- **Tope de contacto por espacio y no por persona** (`docs/capacidades.md`, "Trampas conocidas").
- **Avisos que a veces no salen a su hora** (1 o 2 de cada 95 corridas, dos rondas): causa desconocida; desde
  `2b4afbf` cada intento fallido deja un incidente y el informe de la ronda lo muestra.
- **Una prueba intermitente** en `tests/motor tests/conversaciones` (una falla sin nombre en una corrida, dos
  repeticiones en verde, 2026-10-07); quizás la del indicador de escritura.
- **Advertencias de RDD sin arreglar** (2026-10-07 y 08), casos de borde: el borrador del streaming puede
  quedar visible si falla el envío inmediato del mensaje final; un valor raro del margen vuelve a 10 minutos;
  los álbumes por el webhook; una corrección después de dado el motivo; cómo se decide "en el medio se habló
  de otra cosa".
- **De la Fase C (revisiones y la impugnación del 2026-10-08):** el segundo recordatorio a quien aprueba
  anuncia el día en que se entera quien está arriba contando desde que se guardó, no desde que salió; la
  página del tablero se arma fuera de la guarda (la de la tarea ya no); advertencias de casos de borde de
  cada porción, listadas en `odd/tasks/fase-c.md`.
- **Formato:** la cocina parte los renglones largos y separa el cierre (`c304b23`); quedan, de la IA,
  un título pegado a la tarea y una oración después de la pregunta (el chequeo del corredor lo mide).
