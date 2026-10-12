# Estado actual

**Alcance:** Leda es un producto de gestión de proyectos multi-tenant. CoreWork es
su primer cliente, no su definición.

**Última actualización documental:** 2026-10-12, tarde: la prueba por Telegram de la Fase C pasó y la rama del Motor está en `main`.

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

## Punto exacto para retomar (2026-10-12)

**Dónde:** rama `feat/motor-de-conversacion`, carpeta `D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion`,
subida a `origin` al cierre del 2026-10-12. Plan de la Fase C: [`../odd/tasks/fase-c.md`](../odd/tasks/fase-c.md) (las
decisiones del usuario 1 a 76 y la lista de tareas en "Próximo paso"); la plataforma, en el
[ADR 0022](decisions/0022-plataforma-web-de-tareas.md).

**Antes de nada:** comprobar PostgreSQL (`pg_isready -h localhost -p 5432`). Si está caído, levantarlo con
`levantar-postgres.bat` (o `pg_ctl ... start`, fuera del sandbox). Si `pg_ctl` dice que otro servidor puede
estar en ejecución, cerrar los procesos `postgres` colgados y reintentar. Comprobar que no quede un escuchador
viejo corriendo.

**Lo hecho el 2026-10-11 y el 2026-10-12:**
- Decisiones 65 a 73, construidas; los apodos (ADR 0020), completos; el orden de las jugadas de un
  mensaje (`f0d18e6`).
- **El formato lo da la cocina** (decisión 74, `c304b23`): de 87 fallas en 35 corridas a 15; las que
  quedan son contenido de la IA.
- El corredor compara las jugadas y los hechos sin mirar el orden (`1079b18`) y un paso admite varias
  lecturas (`ca5c38f3`).
- Decisiones 75 (la 48 paso 10 sin jugada vale) y 76 (repetir el nombre contesta la pregunta del
  apodo).
- Cada commit de código, revisado por RDD y aprobado. Detalle en el plan y la bitácora.
- **El ADR 0022 de la plataforma web, aceptado** (`912eb413`): producto (1 a 10), técnica (11 a 16),
  la misma tecnología que la HMI (17) y el aspecto (18), elegido en el lienzo de diseño
  https://claude.ai/artifact/VwC3sCvufFZ7DUkv3yJt7f: la "9 · Terminal", sobria, oscura y de letra de
  máquina, con color sólo en los estados que tienen algo.

**Lo que sigue:**
1. **La prueba por Telegram: pasó** (2026-10-12, pasos 1 a 48; usuario: "paso super bien, las
   correcciones son menores"). Resultado en la bitácora; sus hallazgos, en las decisiones 77 a 79
   de `odd/tasks/fase-c.md` (sin nombre ni hora en los avisos a otros, "consultar", un ícono por
   estado) y la lista que les sigue, cada uno primero como conversación de prueba. La rama del
   Motor pasó a `main` por avance rápido (`270a38a`, subido).
2. **La plataforma, porción 1: construida la noche del 2026-10-12** en la rama `feat/plataforma`
   (carpeta `D:\Proyectos\Leda-PM-worktrees\plataforma`, subida a `origin` en `b1e500b2`), sin tocar la
   conversación: enlace de un solo uso con botón "Entrar" y sesión abierta (`0057`), quién ve qué
   (`0058`), la cadena de esperas (`0059`), la API interna, la web con el aspecto "9 · Terminal" y los
   comandos de consola. Cada commit de código, revisado por RDD y aprobado; garantías en verde. Plan,
   evidencia y **ocho preguntas para el usuario** ("Para decidir", con ejemplos) en
   `odd/tasks/plataforma-p1.md` de esa rama. El 2026-10-12, de día: las ocho preguntas, contestadas y
   construidas (P1-6), y la **porción 2** (la puerta de administración y la carga de tareas, con
   vista de escritorio; `odd/tasks/plataforma-p2.md`), adelantada sin la prueba de la porción 1 en el
   celular por decisión del usuario; rama subida en `c52269a`. **Punto exacto:** el usuario hace
   primero la prueba por Telegram; cuando avise, y con su visto bueno: respaldo de `leda_motor`,
   migraciones hasta la `0064`, juntar las ramas, que Leda ofrezca el acceso por chat y la prueba de las
   dos porciones en el celular y la computadora (túnel o HTTPS, sólo con su permiso). Faltan del
   usuario: el nombre del bot del equipo (`bot_usuario` en el pack) y, de a una, las preguntas de
   "Para decidir" de `odd/tasks/plataforma-p2.md` (quién crea los objetivos, si las esperas van en el
   formulario, quién "decidió" la tarea) y si el enlace de entrada vence (recomendado: 24 horas).
3. **En observación:** la 35 paso 18 (1 de 5 el 2026-10-11; no volvió a pasar en las rondas del
   formato).

**La IA real:** una ronda por vez y ninguna repetición sin preguntarle al usuario. La lanza el coordinador
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

**`leda_motor`:** recreada de nuevo el 2026-10-12 a la madrugada para la prueba por Telegram, porque la
prueba anterior había dejado "Programar PLC" entregada y "Dashboard de lotes" terminada. Respaldo previo
`db/respaldos/leda_motor-antes-recrear-prueba-telegram-20261012.dump` (`pg_restore --list` sin error).
Pasos de la D6 (`esquema --recrear`, `importar corework --activar`, `feriados`, `modelo gpt-6-sol
--proveedor chatgpt`, `sembrar` con una semilla temporal fuera del repositorio con los criterios concretos,
`administrador corework`, aviso previo de 3 días hábiles) y `reloj corework volver`. Quedan 12 tareas
(6 asignadas, 6 en curso) que vencen el vie 16/10, las cuatro del guion como él las describe, sin apodos.
Los chats de Telegram vienen del pack: no se pierden; igual conviene el `/start` y el "hola" del guion.
El usuario autorizó ponerla al día o recrearla cuando haga falta, con respaldo previo; nunca `leda` ni
`leda_flujo`.

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

**Después:** la Fase C, cerrada con la prueba por Telegram del 2026-10-12 (quedan sus correcciones), y la plataforma web, con su
ADR 0022 aceptado. No hay equipo real hasta que el usuario lo diga.

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
- **Migraciones:** hasta `0025` en `main`, más `0030` a `0056` en la rama. La `0032` borra las tablas del alta.
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
- Repositorio `arields85/leda` (público). `origin/main` está en `270a38a` (2026-10-12): la rama del Motor
  llegó por avance rápido el 2026-10-07 (221 commits) y el 2026-10-12 (396 commits, con la Fase C),
  sin atribuciones ni secretos.
- La rama del Motor se sube al cerrar cada tramo.
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
| Rama del Motor, con las decisiones 24 a 55 y la porción 5 (`c06fa6d`) | `pytest tests/motor tests/garantias tests/conversaciones tests/test_administrador_plataforma.py` | 2026-10-10 | 1740 passed |
| Rama del Motor, ídem | `correr --ia guionada --veces 1` (en seco) | 2026-10-10 | 45 de 45 bien |
| Rama del Motor, con los apodos (dos porciones), el cupo y las 48 y 49 (`e4d4f3a`) | `pytest -q` (suite completa) | 2026-10-11 | 2350 passed (30 min) |
| Rama del Motor, ídem (`65086af`) | `correr --ia guionada --veces 1` (en seco) | 2026-10-11 | 47 de 47 bien |
| Rama del Motor, con las decisiones 65 a 73 y el orden de las jugadas (`f0d18e6`) | `pytest -q tests/motor` | 2026-10-11 | 1302 passed |
| Rama del Motor, ídem | `pytest -q tests/garantias` | 2026-10-11 | 475 passed |
| Rama del Motor, ídem | `pytest -q tests/conversaciones` | 2026-10-11 | 194 passed |
| Rama del Motor, ídem | `correr --ia guionada --veces 1` (en seco) | 2026-10-11 | 48 de 48 bien |

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
