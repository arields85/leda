# Estado actual

**Alcance:** Leda es un producto de gestión de proyectos multi-tenant. CoreWork es
su primer cliente, no su definición.

**Última actualización documental:** 2026-10-09, cierre a la mañana: la C-5, la C-6 (por persona) y la
C-7 construidas y revisadas; las decisiones del usuario 24 a 52.

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

## Punto exacto para retomar (2026-10-09, mañana, con el usuario)

**Dónde:** rama `feat/motor-de-conversacion`, carpeta `D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion`.
Plan: [`../odd/tasks/fase-c.md`](../odd/tasks/fase-c.md): las decisiones del usuario 1 a 52 (**todas
contestadas**), el registro de cada unidad y la lista de tareas en "Próximo paso".

**Antes de nada:** comprobar PostgreSQL (`pg_isready -h localhost -p 5432`); al cerrar la sesión se apaga. Si
está caído, levantarlo con `levantar-postgres.bat` (o `pg_ctl ... start`, fuera del sandbox). Si `pg_ctl` dice
que otro servidor puede estar en ejecución, cerrar los procesos `postgres` colgados y reintentar. Comprobar que
no quede un escuchador viejo corriendo.

**Lo hecho la noche del 2026-10-09 (sola, con el usuario dormido):** la D5b (decisión 21,
conversación 30, `0040`), la `0041` (RLS forzado en cinco tablas de configuración y una prueba que
recorre todas), pedir el enlace a la página por chat (conversación 31), la C-5 entera
(perseguir un bloqueo, decisiones 4 a 7; conversaciones 32 a 36, `0042` a `0044`), el pedido de estado
de la C-6 (conversación 37; el informe al grupo, `PENDIENTE`) y la C-7, delegar
(conversación 38, `0045`). Con el usuario a la mañana: sus decisiones 24 a 52, los pedidos para la plataforma (jerarquía,
avisos de cada uno, la vista de todo) y la C-8 (ausencias, para más adelante). Todo revisado por
tramos y subido (`b21053c`); suite completa sobre `e082010`, 1857 passed.

**Lo que sigue (pedido del usuario: avanzar todo lo posible solo, sin esperar pruebas):**
1. **Construir las decisiones 24 a 52** (plan, "Preguntas al usuario"; la 30, la 40, la 43, la 45 y
   la 52 no piden código), con test primero, una porción por grupo: C-5 (24, 34 a 42, 47 a 49,
   51), C-7 (26 a 28), D5b (29, 50), C-6 (31, 32, 44, 46) y el enlace (33).
2. **El informe al grupo de la C-6** (decisión 25): el usuario crea el grupo en Telegram; falta el
   camino de un aviso al grupo y ver cómo toma Leda su identificador.
3. **Las preguntas al usuario están todas contestadas** (decisiones 24 a 52); las nuevas, de a una y
   con ejemplos simples.
4. **La porción 5:** el acceso del administrador por el bot de administración.
5. **Las pruebas pendientes van juntas, en una tanda posterior** (pedido del usuario): la IA real
   sobre la 03, 05, 21, 23, 27, 28 y 30 a 38 (una vez, sin repetir sin preguntar) y la prueba por
   Telegram, con `leda_motor` al día hasta la `0045` (respaldo previo; autorizado) y el guion en
   tandas cortas de unos 15 minutos.

**La IA real:** antes de cada ronda, comprobar el cupo (`leda chatgpt estado`); una ronda por vez y ninguna
repetición sin preguntarle al usuario. El corredor se corta solo al primer error de cupo (sale con 4). Si se
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

**`leda_motor`:** recreada el 2026-10-08 (D6) con las tareas de la prueba (vencen el viernes 16/10);
respaldo `db/respaldos/leda_motor-antes-fase-c-d6-20261008.dump`. Le falta la `0039`. El usuario autorizó
ponerla al día o recrearla cuando haga falta, con respaldo previo; nunca `leda` ni `leda_flujo`.

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

**Después:** la Fase C y la plataforma web (decisiones del usuario: van después de M3). No hay equipo real
hasta que el usuario lo diga.

## Qué quedó congelado o superado

Lo anterior al Motor no se retoma: los flujos A, B y C1 a C6 (A y B ya borrados de la rama), las tareas del alta
por chat (0-35, 0-36, P-1c, P1-P7, 0-29, 0-17, 0-14 y las demás), el paso de circuitos al flujo C6, R11, R12 y el
validador de invariantes. Destino de cada uno:
[`historial/STATUS-hasta-M1.md`](historial/STATUS-hasta-M1.md), "Qué quedó congelado o superado".

## Decisiones pendientes del usuario

- **Copiar el respaldo a la nube o a otro disco.** El `git bundle` del repositorio entero, con la rama congelada
  `feat/flujo-de-un-mensaje` y todas las etiquetas, está en
  `D:\Proyectos\Leda-PM-respaldos\leda-repositorio-completo-20261007.bundle` (2026-10-07, verificado), en el
  mismo disco.
- **El archivo global `~/.claude/CLAUDE.md`** (unos 71.300 caracteres, de gentle-ai) más lo que carga el
  proyecto suman unos 138.700 de 150.000 (`LC_ALL=C.UTF-8 wc -m`, 2026-10-09, con el documento del Motor
  reducido).
- **`PENDIENTE` dentro de los ADR y del plan:**
  - si Leda avisa que se cargaron tareas (ADR 0017, decisión 2);
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
- **Migraciones:** hasta `0025` en `main`, más `0030` a `0045` en la rama. La `0032` borra las tablas del alta.
  Cada una tiene su rollback y su ensayo de paridad.
- **Seguridad de la base:** `row level security` forzado en todas las tablas con alcance de espacio.
  `PENDIENTE`: un ensayo de propiedad sobre un clúster limpio.
- **Las pruebas de garantías** están en `tests/garantias/`, con fronteras que impiden importar código viejo. Las
  del motor, en `tests/motor/`. El corredor y las 20 conversaciones de prueba, en `tests/conversaciones/`
  (`python -m tests.conversaciones.correr --ia …`).
- **La salida con formato:** la IA escribe `**negrita**`, párrafos y "• "; el outbox guarda ese texto y el
  despachador lo manda como texto plano con entidades de Telegram (`salida.formatear`), sin `parse_mode`.
- **Lo que lee la IA al redactar:** los nombres de los datos se traducen a palabras de todos los días
  (`hechos.para_redactar`); adentro no cambian.
- **`prueba_chica/`** se borró el 2026-10-07 (`c43e3e5`); el lector de turnos es `leda.motor.leer`.

**Git:**
- Repositorio `arields85/leda` (público). `origin/main` está en `6ee287a` (2026-10-08); el motor llegó a `main` por avance
  rápido el 2026-10-07 (221 commits, sin atribuciones ni secretos).
- La rama del Motor se sube al cerrar cada tramo; lo posterior a `6ee287a` llega a `main` cuando la
  entrega y la aprobación pasen con la IA real.
- Etiquetas: `respaldo-flujos-antes-de-d`, `respaldo-main-antes-de-d`, `respaldo-0-36-en-pausa`,
  `archivo-c4-medicion`, `archivo-flujo-c6`, `archivo-prueba-0-35` y `respaldo-antes-de-partir-limpieza`
  (todas locales salvo las del 2026-10-04).
- Ramas congeladas: `feat/flujo-de-un-mensaje` y `auxiliar/alta-y-google`, con sus carpetas en
  `Leda-PM-worktrees`. Las carpetas `c4-medicion`, `flujo-c6` y `prueba-0-35` se borraron el 2026-10-07; sus
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

**Conversaciones con la IA real** (bitácora de flujos):
- La ronda 3 de la prueba chica dio 85 de 85.
- La regresión del motor definitivo con sol por OpenRouter dio 89 de 90.
- Con sol por la suscripción dio 90 de 90; con las palabras de todos los días, 94 de 95 y 95 de 95; con el
  formato de los mensajes, 100 de 100 (20 conversaciones); con el margen para corregir, 100 de 100 en las 01 a 20
  y la corrección de la 25 bien 5 de 5. El mensaje sin puntuación del usuario se lee mal 5 de 5.

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
- **El escuchador** lo corre el usuario en su terminal; las tareas en segundo plano del agente se cortan por
  tiempo.

## Riesgos prioritarios

1. **El outbox está atado a un transporte:** `message_outbox` tiene `chat_id` y `telegram_message_id` y no tiene
   canal; bloquea toda superficie no conversacional.
2. **Un límite de transporte decide validez de negocio:** `telegram_utf16_units` (`salida.py`).
3. **No hay grafo de transiciones de estado:** `actualizar_estado` acepta cualquier destino del enumerado.
4. **`confirmar_borrador_tarea` fija el espacio con el valor que recibe:** acotada a `leda_gateway`, pero es el
   patrón que la frontera rechaza.
5. **La IA por la suscripción del usuario** sirve sólo para uso personal. Depende de un servicio no oficial de
   OpenAI, que puede cambiar sin aviso. En la etapa comercial, cada cliente pone su proveedor.
6. **Ningún equipo real usó Leda:** todas las pruebas fueron con datos ficticios y un evaluador que conoce el
   guion.

Contrastar los riesgos 1 a 4 contra el símbolo, no contra números de línea.

## Deudas registradas

- **Producción:**
  - Faltan cola de entrada, pool de conexiones, observabilidad, respaldo y restauración.
  - El webhook atiende un mensaje a la vez, bajo un candado global, y el candado de cada mensaje sigue tomado
    mientras responde la IA (revisión de la E3-7).
- **Sesión de ChatGPT:** falta un candado sobre el archivo, para que dos procesos no la renueven a la vez.
- **Honestidad en casos de borde** (revisión de la E3-6):
  - un aviso cuya hora ya pasó se anuncia con esa hora (la prueba de M3 lo mostró una vez);
  - el aviso al administrador;
  - los códigos de `hechos`.
- **Una pregunta "para después" vuelve días más tarde en medio de otro tema** (prueba de M3).
- **Vencimiento en fin de semana:** la escalera alrededor de un fin de semana está probada
  (`tests/motor/test_escalera_fin_de_semana.py`, 2026-10-09: un viernes escala el miércoles, el
  aviso previo cruza fines de semana y feriados, la comprimida no saltea pasos). `PENDIENTE` de
  decisión: un vencimiento que cae sábado o domingo no tiene regla; hoy la escalera cuenta como si
  venciera el viernes anterior (pide el estado ese viernes y escala el miércoles).
- **`apscheduler`** sigue en `pyproject.toml` y ya no lo usa nadie.
- **Contexto de la IA:** comparar el contexto amplio con variantes reducidas; requiere ADR antes de operar en
  internet.
- **Alta de un segundo cliente:** el proceso no está definido.
- **Autoridad sobre `cancelada`** (T2b): `PENDIENTE` de decisión.
- **Reintento del despachador:** puede reordenar partes de una respuesta partida.
- **Tope de contacto por espacio y no por persona** (`docs/capacidades.md`, "Trampas conocidas").
- **Avisos que a veces no salen a su hora** (1 o 2 de cada 95 corridas, dos rondas): causa desconocida; desde
  `2b4afbf` cada intento fallido deja un incidente y el informe de la ronda lo muestra.
- **`conversation_state.mostrado_para_confirmar`** no lo lee nadie: por eso `test_capacidades` exime las
  tablas del motor (`TABLAS_DEL_MOTOR`). Decidir para qué es o borrarla.
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
- **Formato:** a veces la IA junta dos ideas en un renglón o hace dos preguntas al cierre (el chequeo del
  corredor lo mide).
