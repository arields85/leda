# Estado actual

**Alcance:** Leda es un producto de gestión de proyectos multi-tenant. CoreWork es su primer cliente, no su
definición.

**Última actualización documental:** 2026-10-15, cierre de la noche (STATUS reducido; ver "Punto exacto para
retomar").

Versiones anteriores (historia, no estado vigente ni instrucción), en `historial/`:
[`STATUS-hasta-2026-09-30.md`](historial/STATUS-hasta-2026-09-30.md),
[`STATUS-hasta-2026-10-04.md`](historial/STATUS-hasta-2026-10-04.md),
[`STATUS-hasta-M1.md`](historial/STATUS-hasta-M1.md), [`STATUS-hasta-M3.md`](historial/STATUS-hasta-M3.md) y
[`STATUS-hasta-2026-10-15.md`](historial/STATUS-hasta-2026-10-15.md) (con la línea base de pruebas completa, la
historia de `leda_motor` y las deudas en detalle).

## Resumen

La capa de datos y de garantías funciona: aislamiento entre clientes, estado como proyección de eventos,
confirmaciones con vista previa, outbox y auditoría. La conversación la lleva **el Motor**
([`../AGENTS.md`](../AGENTS.md), "Nombres que usamos"): la IA elige jugadas de una lista cerrada y el código las
ejecuta (ADR 0017 y 0018). M1, M2 y M3 cumplidos (2026-10-04 a 07); la Fase C cerrada (2026-10-12/13). Leda
conversa con `python -m leda escuchar corework`, con GPT-6 sol por la suscripción de ChatGPT del usuario (uso
personal). Ahora se construye la plataforma web por jerarquía y la Mini App.

## Punto exacto para retomar (2026-10-15, cierre de la noche)

**Dónde:** rama `feat/motor-de-conversacion`, carpeta `D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion`.
Unidad en curso: [`../odd/tasks/plataforma-jerarquias.md`](../odd/tasks/plataforma-jerarquias.md) (ADR 0023 en
porciones J1 a J7; la Mini App, ADR 0024).

**Primero en la sesión nueva** (usuario, cierre del 2026-10-15):
1. **Arrancar la J7 de fondo**, de la J7-6 en adelante, una porción tras otra sin esperar al usuario (escritor
   delegado, prueba primero, RDD, documento de la unidad; las dudas de producto van a "Para decidir"). La J7-6
   **no se empezó**: lo de fondo muere al cerrar la sesión.
2. **En primer plano, seguir puliendo el diseño** con el usuario (ver "Diseño").

**Antes de nada:** `pg_isready -h localhost -p 5432`. Si no responde aunque `pg_ctl status` diga que corre,
cerrar con `taskkill /F` todos los `postgres.exe` y arrancar con `pg_ctl ... start -l` a un registro nuevo, fuera
del sandbox. Antes de una ronda con la IA real, comprobar que no corra el escuchador del usuario (`tasklist`): si
corre, la ronda espera; el escuchador es del usuario.

**Hecho:** J1 a J4 y la Mini App cerradas; J7-0 a J7-5b (equipo que cuadra, el pack sólo arma un equipo vacío,
ver el equipo, áreas, alta con enlace, nombre por espacio). El 2026-10-15 a la noche: RDD de `9d871545` aprobada
en tres pedazos; alta duplicada corregida (`a71d2623`); `0085` aplicada a `leda_motor`; nombres de pestañas
estándar en todo (`da249f05`, `12c33af7`): referente «Mis tareas · Mi área · Mis pedidos», Dirección «Mis tareas ·
Áreas · Equipo». Todas las decisiones de la J5, la J6 y la J7 están tomadas (DECIDIDO/CONTESTADO en el documento
de la unidad; ADR 0025 aceptado).

**Lo que sigue a construir, en este orden** (usuario, 2026-10-15): 1. la J7 (armar el equipo desde la web);
2. configurar el equipo desde la web (horario, feriados, cadencias, informe, evidencia por área, límites, sesión de
administración, exportar como respaldo; decisiones de a una antes del código); 3. ausencias y suplente de
Dirección; 4. la J5; 5. la J6; 6. mejoras chicas («Mi espacio», cancelar y reabrir, hallazgos, respuesta pendiente
cuando falla la IA). Falta que el usuario mire en la compu la MA-7 y "te la pidió". Sin el usuario: las
advertencias de RDD de cada entrada; el grafo no se toca sin él (dos arreglos seguidos).

**Diseño** (con impeccable siempre: sorteo + página de decisión para pantallas nuevas; las extensiones heredan;
nunca a mano). Todo en `.impeccable/surfaces/web-src-app-tsx.md`. La **r8 «sobria»** (referencias del usuario:
casi negro con degradado, bandas con filetes, cifras finas, Kanit en `.impeccable/mocks/fonts/kanit/`, fondo con
huecos animado, zona urgente fija que se achica, vidrio, contadores que filtran) cubre todas las pantallas:
`.impeccable/mocks/decision/r8-sobrio.html` (Mis tareas), `-mi-area`, `-pedidos`, `-direccion`, `-areas`,
`-area-it`, `-equipo`, `-tarea`; la r7 se guarda. **Próximo:** el usuario decide si la r8 pasa a oficial (el
documenter reescribe `DESIGN.md`, aún en la r7, y `.impeccable/design.json`, que describe la barra flotante);
después, pasarla a `web/`. La tarea abierta necesita que la historia viaje a la Mini App (`detalle_en_json`).
El script de `live` se inyecta en las muestras: nunca commitearlo; los bocetos de la página de decisión se
escriben **después** de levantarla.

**En cada porción:** explorar lo que existe, conversación de prueba antes que el código cuando toca el chat,
escritor delegado con la regla de LF, prueba primero, RDD por commit (`tools/rdd_ciclo.py <carpeta> <base>` en un
worktree temporal; un commit grande se parte en tramos), la ronda real de las conversaciones afectadas, y al
cerrar cada tarea el documento de la unidad, este punto, Engram y la memoria.

**Acuerdos:** las decisiones de cada porción se traen al principio, de a una y en texto; los avisos cuentan lo
que vale ahora; un cambio de plazo trae el informe de "en qué afecta"; pedir a Leda que abra la app no lleva
botón (dice que toque «Mi espacio»). El agente encadena el trabajo técnico y sólo para ante decisiones de
producto. Commits por unidad sin atribución; la rama se sube a `arields85/leda`; `main` lo decide el usuario. RDD
con consentimiento permanente; los informes generados y los commits sólo de documentos no se revisan.

**La IA real:** autorizada para todas las pruebas, sin preguntar; una ronda por vez y sólo los casos afectados.
La lanza el coordinador en segundo plano con `salida=$?` del corredor; el corredor se corta solo al primer error
de cupo (sale con 4) y entonces todo lo de la IA real espera a que el usuario cambie de cuenta a mano. Una ronda
completa de las 29 cuesta unas 1.500 a 1.800 llamadas.

**Para probar en el celular:** el agente levanta la web
(`.venv\Scripts\python.exe -m uvicorn leda.entrada:app --host 127.0.0.1 --port 8000 --no-access-log`) y el túnel,
y pone la dirección en `LEDA_BASE_URL` del `.env`. Si la Mini App dice "No se pudo entrar", reiniciar la web.
Prueba por Telegram (guion `docs/product/guion-telegram-fase-c-parte-1.md`): el escuchador lo corre el usuario
(`.venv\Scripts\python.exe -m leda escuchar corework`); el reloj, `.venv\Scripts\python.exe -m leda.motor.reloj
corework adelantar|estado|volver`; los turnos, `.venv\Scripts\python.exe -m leda.motor.leer corework --completo`.
Nunca el escuchador y una ronda del corredor a la vez, ni una ronda real mientras se edita `src/`.

**`leda_motor`:** en la `0085` (último respaldo `db/respaldos/leda_motor-antes-0085-20261015.dump`). Autorizado
ponerla al día o recrearla cuando haga falta, con respaldo previo y ensayo en una copia descartable, aplicando con
`psql -v ON_ERROR_STOP=1 -f` como `postgres`; nunca `leda` ni `leda_flujo`.

## Decisiones pendientes del usuario

- Si la r8 «sobria» pasa a ser la dirección oficial del diseño.
- Las que deje el agente trabajando solo: `../odd/tasks/plataforma-jerarquias.md`, "Para decidir al despertar".
- Copiar el respaldo del repositorio (`D:\Proyectos\Leda-PM-respaldos\leda-repositorio-completo-20261007.bundle`)
  a la nube o a otro disco.
- La carga de instrucciones al iniciar (el `~/.claude/CLAUDE.md` global de gentle-ai, unos 71.300 caracteres, más
  lo del proyecto) roza el límite de 150.000: medir con `LC_ALL=C.UTF-8 wc -m` cuando cambien los importados.
- `PENDIENTE` en los ADR y el plan: si quien destraba dice que no le corresponde (3a); preguntarle al referente
  sin dejar de ser Leda la PM; cómo llega el tono de cada cliente a la IA; si cancelar un borrador deja
  auditoría; la autoridad sobre `cancelada` (T2b).

## Qué quedó congelado o superado

Lo anterior al Motor no se retoma: los flujos A, B y C1 a C6, las tareas del alta por chat (0-35, 0-36, P-1c,
P1-P7, 0-29, 0-17, 0-14 y las demás), el paso de circuitos al flujo C6, R11, R12 y el validador de invariantes.
Destino de cada uno: [`historial/STATUS-hasta-M1.md`](historial/STATUS-hasta-M1.md).

## Estado comprobado

- **Código:** el motor de conversación es `src/leda/motor/` (3 capas, escuchador, `recibir.py` compartido con el
  webhook, `chatgpt.py`); la entrada HTTP, `src/leda/entrada.py`; la web, `web/` (React y TypeScript). Los flujos
  A y B están borrados. Cada efecto deja su fila en `audit_log` con `pack_hash` y `nucleo_hash`.
- **Migraciones:** hasta `0025` y de `0030` a `0056` en `main`; de `0057` a `0085` en la rama. Cada una con su
  rollback y su ensayo de paridad.
- **Seguridad de la base:** `row level security` forzado en todas las tablas con alcance de espacio; ensayo de
  propiedad sobre un clúster limpio (2026-10-15, `tools/ensayo_propiedad.py`; T8 de
  `odd/tasks/aislamiento-entre-clientes.md`).
- **Pruebas:** garantías en `tests/garantias/`, motor en `tests/motor/`, el corredor y las conversaciones de
  prueba en `tests/conversaciones/` (`python -m tests.conversaciones.correr --ia …`). Última suite completa:
  3286 passed (2026-10-13, `eaf84ed4`, `LEDA_BASE_URL= LEDA_GEMINI_API_KEY= pytest -q`, 31 min). Web: `npm test`
  370 passed y `npm run build` bien (2026-10-15). La línea base histórica está en el archivo del 2026-10-15.
- **Conversaciones con la IA real:** las cifras y la conclusión vigente están en la bitácora de flujos. Una
  suite en verde no es evidencia de que la conversación funcione (`AGENTS.md`, punto 12).
- **Git:** repositorio `arields85/leda` (público); `origin/main` en `80d6945` (2026-10-12); la rama del Motor se
  sube al cerrar cada tramo. Etiquetas de respaldo: `respaldo-flujos-antes-de-d`, `respaldo-main-antes-de-d`,
  `respaldo-0-36-en-pausa` y las de archivo. Ramas congeladas `feat/flujo-de-un-mensaje` y
  `auxiliar/alta-y-google`, con sus carpetas en `Leda-PM-worktrees`.

## Operación

- Sin producción, Docker ni staging. Telegram real sólo con datos ficticios (cuentas de prueba Ariel, Ismael y
  Marcos, que opera el usuario).
- Bases locales: `leda` (de `main`), `leda_flujo` (rama congelada) y `leda_motor` (la del `.env` de la carpeta del
  Motor); los roles `leda_*` son compartidos.
- Bots del Motor: el del equipo y el de administración, con sus tokens en el `.env` de la carpeta, que el agente no
  lee. La sesión de ChatGPT está en `~/.leda/chatgpt.json` y se renueva sola.

## Riesgos prioritarios

1. **El outbox está atado a un transporte:** `message_outbox` tiene `chat_id` y `telegram_message_id` y no tiene
   canal.
2. **Un límite de transporte decide validez de negocio:** `telegram_utf16_units` (`salida.py`).
3. **El grafo de transiciones, en parte:** desde la `0079` la base exige lo de la mecánica §3; los demás saltos de
   `actualizar_estado` esperan decisiones del usuario.
4. **`confirmar_borrador_tarea` fija el espacio con el valor que recibe** (acotada a `leda_gateway`).
5. **La IA por la suscripción del usuario** es sólo para uso personal y depende de un servicio no oficial.
6. **Ningún equipo real usó Leda.**

Contrastar los riesgos 1 a 4 contra el símbolo, no contra números de línea.

## Deudas registradas

El detalle de cada una está en [`historial/STATUS-hasta-2026-10-15.md`](historial/STATUS-hasta-2026-10-15.md),
"Deudas registradas".
- Lenguaje: queda lo técnico (`NO_EFFECT_STATUS`, vistas previas de `herramientas.py`, `cli.py` del operador).
- Producción: cola de entrada, pool de conexiones, observabilidad, respaldo y restauración; el webhook atiende un
  mensaje a la vez.
- Honestidad en casos de borde (aviso con hora ya pasada, aviso al administrador, códigos de `hechos`).
- Una pregunta "para después" vuelve días más tarde en medio de otro tema.
- Contexto de la IA (comparar variantes; ADR antes de internet); alta de un segundo cliente sin proceso.
- Reintento del despachador que puede reordenar partes; tope de contacto por espacio y no por persona.
- Avisos que a veces no salen a su hora (1 o 2 de cada 95; cada intento fallido deja un incidente).
- Una prueba intermitente en `tests/motor tests/conversaciones`.
- Advertencias de RDD sin arreglar (Fase C y anteriores; listadas en `odd/tasks/fase-c.md`) y de formato de la IA.
