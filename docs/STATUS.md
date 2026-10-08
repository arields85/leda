# Estado actual

**Alcance:** Leda es un producto de gestión de proyectos multi-tenant. CoreWork es
su primer cliente, no su definición.

**Última actualización documental:** 2026-10-08, sesión con el usuario: las decisiones 10 a 21 de la Fase C,
las unidades D1 a D5 de la C-3d construidas y revisadas, y la D6 (la ronda con la IA real) en curso.

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
un atraso, garantías y comprensión 5 de 5 en las 01 a 20 y la 24 (2026-10-08). La entrega y la aprobación por
chat (Fase C) están construidas y todavía no pasan con la IA real (bitácora de flujos).

## Punto exacto para retomar (2026-10-08, sesión con el usuario)

**Dónde:** rama `feat/motor-de-conversacion`, carpeta `D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion`.
Plan: [`../odd/tasks/fase-c.md`](../odd/tasks/fase-c.md), la C-3d (unidades D1 a D6, con el registro de cada
una) y las decisiones del usuario 10 a 21.

**Antes de nada:** comprobar PostgreSQL (`pg_isready -h localhost -p 5432`); al cerrar la sesión se apaga. Si
está caído, levantarlo con `levantar-postgres.bat` (o `pg_ctl ... start`, que el agente corre fuera del
sandbox). Si `pg_ctl` dice que otro servidor puede estar en ejecución, cerrar los procesos `postgres`
colgados y reintentar. Comprobar que no quede un escuchador viejo corriendo.

**Lo hecho el 2026-10-08:** el usuario decidió las preguntas 10 a 21 (en `odd/tasks/fase-c.md`) y se
construyeron D1 a D5, revisadas por commit:
- **D1:** el comparador del corredor. **D2:** Leda no nombra a quien aprueba por su cuenta (sólo si le
  preguntan); "revisar" y "describir".
- **D3:** la entrega contra el criterio de aceptación (pregunta sólo lo que falta, con un ejemplo sacado del
  criterio, y no entrega hasta cubrirlo), entregar una tarea sin arrancar y la pieza retirada. Migración
  `0038`.
- **D4:** "¿cuál de las dos?" una sola vez; las entregas para revisar en una lista con un botón [Ver …] por
  tarea; el aviso va a quien aprueba al salir.
- **D5:** los avisos esperan 30 minutos desde lo último que escribió la persona (`no_interrumpir_minutos`) y
  nunca salen junto con una pregunta sin contestar.

**En curso al cerrar este registro: D6.** La ronda con la IA real de las 29 conversaciones, después
`leda_motor` al día (migraciones `0034` a `0038` y el pack, con respaldo previo) y el guion de la prueba por
Telegram (`docs/product/guion-telegram-fase-c-parte-1.md`). Si se cortó, mirar qué dejó escrito antes de
repetir nada.

**Lo que sigue:**
1. **El resultado de la D6.** Las fallas reales de Leda se tratan como regla general, con su conversación de
   prueba primero (`AGENTS.md`, "Hallazgos de conversación").
2. **D5b, decisión 21 del usuario** (2026-10-08, opción B; todavía no está escrita en `odd/tasks/fase-c.md`:
   pasarla ahí al empezar). Una pregunta de Leda sin contestar:
   - frena los otros temas de esa persona hasta que Leda la repite, una sola vez, a las 4 horas (ajustable
     desde la plataforma, anotado en `docs/product/plataforma-pendientes.md`);
   - si 4 horas después de la repetición sigue sin contestar y todavía es horario, sale aparte el tema
     siguiente más urgente (ejemplo: 08:55 la entrega del PLC, 12:55 su repetición, 16:55 el tablero que vence);
   - la segunda pregunta guarda la primera "para después": la persona contesta cualquiera de las dos, nombrando
     la tarea, y al cerrarse una el código trae la otra enseguida, en un mensaje aparte (hoy la retoma sólo la IA,
     si le parece);
   - al día siguiente sigue la escalera; varias cosas esperando van de a una, primero la más urgente;
   - el aviso de atraso es "informar", sin nombrar a nadie ("Si mañana sigue igual, voy a informar que está
     atrasada"), nunca "la paso para que te ayuden"; si preguntan a quién, Leda dice el nombre.

   Antes del código: una conversación de prueba con los dos órdenes de respuesta (primero el PLC, primero el
   tablero), corrida con la IA real.
3. **Lo que queda de la parte 1 de la Fase C:** pedir el enlace a la página por chat (una jugada nueva, con su
   conversación de prueba primero), la porción 5 (el acceso del administrador por su bot) y la prueba del
   usuario por Telegram, que cierra la parte 1.
4. **Diez tablas con `workspace_id` sin `row level security`** (lista en `odd/tasks/fase-c.md`): ver si son sólo
   de administración o si les falta, contra la invariante de `AGENTS.md`.
5. **Las partes 2 a 4** (la persecución del bloqueo, las cadencias, delegar) esperan sus preguntas. Delegar ya
   está decidido como funcionalidad (`docs/ROADMAP.md`); al construirlo cambian las respuestas de las
   conversaciones 12 y 19.

**Comandos de la prueba por Telegram** (`.venv\Scripts\python.exe -m …`, desde la carpeta del Motor):
- `leda escuchar corework`: el escuchador. `leda servir`, en otra terminal, para la página de la tarea, con
  `LEDA_BASE_URL=http://localhost:8000` y Telegram Desktop o Web en la PC (decisión 20).
- `leda.motor.reloj corework adelantar|estado|volver`, y `hora HH:MM` para ir a una hora del mismo día. Entre
  salto y salto, esperar 2 minutos: los avisos se revisan una vez por minuto real.
- `leda.motor.leer corework --completo`: el registro de turnos y los avisos guardados.
- **Ojo:** nunca el escuchador y una ronda del corredor a la vez, ni una ronda real mientras se edita `src/`.

**`leda_motor`:** el usuario autorizó de antemano ponerla al día o recrearla cuando haga falta (2026-10-08),
siempre con respaldo previo en `db/respaldos/`. Nunca `leda` ni `leda_flujo`.

**Acuerdos de trabajo** (detalle en la memoria del agente):
- **Autonomía:** el agente encadena todo el trabajo técnico sin preguntar y sólo para ante decisiones de
  producto, que explica con ejemplos completos (el hilo entero, sin cortar mensajes).
- **Commits:** los de cada unidad, sin líneas de atribución. La rama se sube a `arields85/leda` (autorizado);
  `main` lo decide el usuario. Lo posterior a `6ee287a` todavía no se subió.
- **Gasto en IA real:** autorizado.
- **RDD:**
  - Consentimiento permanente. Se revisa por commit con `tools/rdd_ciclo.py <carpeta> <base>`, en una carpeta
    temporal (`git worktree add --detach`), porque ese comando revisa siempre hasta la punta.
  - Los informes generados y los commits sólo de documentos no se revisan.
  - El aviso automático de "revisar la rama entera" excede al revisor y no se corre; tampoco el de cambios sin
    commit de un escritor que está trabajando.

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
- **Delegar por chat:** queda abierto si el referente original tiene que intervenir. La mecánica §7 pide
  re-aprobación ante un cambio de responsable, y el usuario no quiere que la delegación dependa de que Ismael
  toque algo (`docs/ROADMAP.md`).
- **El archivo global `~/.claude/CLAUDE.md`** (unos 71.300 caracteres, de gentle-ai) más lo que carga el
  proyecto quedan al límite de 150.000 (`LC_ALL=C.UTF-8 wc -m`, 2026-10-08).
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
- **Migraciones:** hasta `0025` en `main`, más `0030` a `0032` en la rama. La `0032` borra las tablas del alta.
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
| Rama del Motor, con la C-3d hasta la D5 (`56a3564`) | suite completa | 2026-10-08 | 1607 passed |
| Rama del Motor, ídem | `pytest tests/garantias` | 2026-10-08 | 323 passed |
| Rama del Motor, ídem | `correr --ia guionada --veces 1` (en seco) | 2026-10-08 | 29 de 29 bien |

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
- **Vencimiento en fin de semana:** la escalera no lo tiene probado.
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
