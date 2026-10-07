# Estado actual

**Alcance:** Leda es un producto de gestión de proyectos multi-tenant. CoreWork es
su primer cliente, no su definición.

**Última actualización documental:** 2026-10-07, al cumplir M3 y cerrar la sesión.

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
usuario (proveedor `chatgpt`; uso personal, decisión del usuario). La regresión de las 18 conversaciones de
prueba dio 90 de 90.

## Punto exacto para retomar (2026-10-07, M3 cumplido; sigue el formato de los mensajes)

**Dónde:** rama `feat/motor-de-conversacion`, carpeta `D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion`
(reglas en [`../AGENTS.md`](../AGENTS.md)). El plan de la etapa es
[`../odd/tasks/motor-definitivo.md`](../odd/tasks/motor-definitivo.md).

**Antes de nada:** comprobar PostgreSQL (`pg_isready -h localhost -p 5432`); al cerrar la sesión se apaga. Si
está caído, levantarlo con `levantar-postgres.bat` (o `pg_ctl ... start`, que el agente corre fuera del
sandbox, porque dentro no puede escribir su registro). Con `0xC0000142`, cerrar los procesos `postgres`
colgados y reintentar.

**1. Lo que quedó en marcha al cerrar: las palabras de todos los días** (decisión del usuario, 2026-10-07).
- **La regla:** Leda no nombra los conceptos del sistema, como "previsión", "fecha comprometida" o "pedido de
  estado"; dice el hecho concreto en palabras de todos los días. Viene de la prueba real: Marcos preguntó
  "¿qué es previsión?".
- **Ya commiteado:** la conversación de prueba 19 (`098bc80`, `28f29fc`) y el arreglo en la cocina
  (`230cf7e`). Los informes del rojo y del verde están en `tests/conversaciones/resultados/palabras-*`.
- **Lo primero de la próxima sesión:**
  - `git status` y `git log --oneline -10`.
  - El ayudante se frenó al cerrar la sesión, con la regresión completa a medio correr y anunciando que
    iba a ajustar "los textos y la huella de las instrucciones". No dejó cambios sin commitear: primero
    correr `pytest tests/motor tests/conversaciones` para confirmar que `230cf7e` quedó completo.
  - Si faltan los informes de la regresión completa con `--ia sol-suscripcion` (19 conversaciones por 5),
    correrla. Si están sin commitear, commitearlos.
  - Revisar con RDD los commits `098bc80` a `230cf7e` por tramos, que todavía no tienen revisión.
  - Registrarlo en la bitácora.

**2. Lo siguiente: el formato de los mensajes** (pedido del usuario al aprobar M3, con capturas de antes y
después).
- **El pedido:** los mensajes de Leda son bloques de texto rígidos. Tienen que ser breves y con formato:
  - las tareas y las palabras importantes en negrita;
  - un salto de línea entre párrafos;
  - listas con viñetas cuando hay varias cosas, por ejemplo una persona con sus tareas en el escalamiento.
- **Diseño propuesto:**
  - La IA marca un formato simple (negrita, párrafos y viñetas).
  - La cocina lo convierte al formato de Telegram, escapando todo lo demás y respetando el largo
    (`salida.py` y el despachador; ver si hoy mandan `parse_mode`).
  - La instrucción de redacción describe el trabajo, sin frases de ejemplo.
- **Método:**
  1. Primero, una conversación de prueba.
  2. Después, una prueba del contrato de salida en `tests/garantias`.
  3. Al final, la verificación con `--ia sol-suscripcion` y la próxima prueba por Telegram.

**3. Después:**
- Borrar `prueba_chica/` (cumplió). Antes hay que sacarla de `MOTORES` en `tests/conversaciones/motores.py` y
  reemplazar el lector de turnos: `python -m prueba_chica.leer corework --completo` sigue siendo el único y
  lee `leda_motor`.
- **Llevar la rama a `main`: autorizado** (usuario, 2026-10-07: "se puede llevar la rama a main, decidilo
  vos"). El agente lo deja para el comienzo de la próxima sesión, después de cerrar y revisar las palabras de
  todos los días.
  - **Cómo:** desde `D:\Proyectos\Leda-PM`, que es la carpeta de `main`, avance rápido a la punta de la rama
    (`origin/main` en `e466eb5` es antecesor) y push.
  - Antes, comprobar que no queden líneas de atribución ni archivos sensibles.
- La Fase C del plan, después de M3:
  - los circuitos 7 y 8 (entrega y aprobación), el 5 (cadencias) y la persecución completa de un bloqueo (3a);
  - **delegar por chat**, ya decidido en parte (`docs/ROADMAP.md`, "Anotado para más adelante");
  - el ADR de la plataforma web, antes de su código.

**Comandos de la prueba por Telegram** (`.venv\Scripts\python.exe -m …`, desde la carpeta del Motor):
- `leda escuchar corework`: el escuchador.
- `leda.motor.reloj corework adelantar|estado|volver`, y `hora HH:MM` para ir a una hora del mismo día.
- `leda chatgpt login|estado|salir` y `leda modelo gpt-6-sol --proveedor chatgpt`.
- `prueba_chica.leer corework --completo`: el registro de turnos.
- **Ojo:** nunca correr el escuchador y una ronda del corredor a la vez. Comparten la sesión de ChatGPT, y una
  renovación simultánea puede invalidarla.

**`leda_motor`:** tiene los datos de la prueba de M3 y el reloj en tiempo real. La semilla se cargó con el
vencimiento a 9 días, para que cayera en un día hábil. Respaldo previo:
`db/respaldos/leda_motor-antes-m3-b-20261007.dump`. El modelo activo es `chatgpt / gpt-6-sol`.

**Acuerdos de trabajo** (detalle en la memoria del agente):
- **Autonomía:** el agente encadena todo el trabajo técnico sin preguntar y sólo para ante decisiones de
  producto.
- **Commits:** los de cada unidad, sin líneas de atribución. La rama se sube a `arields85/leda` (autorizado);
  `main` lo decide el usuario.
- **Gasto en IA real:** autorizado.
- **RDD:**
  - Consentimiento permanente. Se revisa por tramos con `tools/rdd_ciclo.py <carpeta> <base>`, en una carpeta
    temporal (`git worktree add --detach`), porque ese comando revisa siempre hasta la punta.
  - Los informes generados no se revisan, y los borrados puros quedaron sin revisar por decisión del usuario.
  - El aviso automático de "revisar la rama entera" excede al revisor y no se corre.

## Próximo paso

**Etapa 1** (diseño) y **Etapa 2** (prueba chica): terminadas, M1 y M2.

**Etapa 3** (limpieza y motor definitivo): terminada, M3 (2026-10-07). Plan y evidencia en
`odd/tasks/motor-definitivo.md`. Quedan sus cierres: las palabras de todos los días, el formato de los
mensajes, borrar `prueba_chica/` y llevar la rama a `main`.

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
- **El archivo global `~/.claude/CLAUDE.md`:** unos 71.000 caracteres, lo maneja gentle-ai. El proyecto carga
  unos 76.000 (`LC_ALL=C.UTF-8 wc -m`, 2026-10-07).
- **`PENDIENTE` dentro de los ADR y del plan:**
  - si Leda avisa que se cargaron tareas (ADR 0017, decisión 2);
  - qué pasa si quien destraba dice que no le corresponde (3a);
  - preguntarle al referente sin dejar de ser Leda la PM;
  - qué hace la persona con una tarea terminada antes del circuito de entrega;
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
  del motor, en `tests/motor/`. El corredor y las 19 conversaciones de prueba, en `tests/conversaciones/`
  (`python -m tests.conversaciones.correr --ia … --motor …`).
- **`prueba_chica/`** sigue en el repositorio como motor de referencia, hasta que se borre.

**Git:**
- Repositorio `arields85/leda` (público). `origin/main` está en `e466eb5`.
- La rama del Motor está subida hasta el cierre de esta sesión. Si quedaron commits del ayudante de las
  palabras de todos los días después del último push, subirlos.
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
| Rama del Motor, sin los flujos A y B (E3-4) | suite completa | 2026-10-06 | 626 passed |
| Rama del Motor, con el proveedor `chatgpt` | suite completa | 2026-10-07 | 1162 passed |
| Rama del Motor | `pytest tests/motor` | 2026-10-07 | 480 passed |
| Rama del Motor | `pytest tests/garantias` | 2026-10-07 | 146 passed |
| Rama del Motor | `pytest prueba_chica` (fuera de la suite) | 2026-10-07 | 356 passed |

**Conversaciones con la IA real** (bitácora de flujos):
- La ronda 3 de la prueba chica dio 85 de 85.
- La regresión del motor definitivo con sol por OpenRouter dio 89 de 90.
- Con sol por la suscripción dio 90 de 90.

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
6. **`main` no tiene el motor** hasta que reciba la rama.
7. **Ningún equipo real usó Leda:** todas las pruebas fueron con datos ficticios y un evaluador que conoce el
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
