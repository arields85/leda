# Estado actual

**Alcance:** Leda es un producto de gestión de proyectos multi-tenant. CoreWork es
su primer cliente, no su definición.

**Última actualización documental:** 2026-10-08, de noche (sesión autónoma): la regresión del motivo con
la IA real, `main` en `6ee287a`, la C-3 de la Fase C construida hasta la porción 4 y su primera ronda con
la IA real.

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

## Punto exacto para retomar (2026-10-08, de noche, sesión autónoma)

**Dónde:** rama `feat/motor-de-conversacion`, carpeta `D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion`
(reglas en [`../AGENTS.md`](../AGENTS.md)). Planes: [`../odd/tasks/fase-c.md`](../odd/tasks/fase-c.md) (lo que
sigue, con el registro de cada porción) y [`../odd/tasks/motor-definitivo.md`](../odd/tasks/motor-definitivo.md).

**Antes de nada:** comprobar PostgreSQL (`pg_isready -h localhost -p 5432`); al cerrar la sesión se apaga. Si
está caído, levantarlo con `levantar-postgres.bat` (o `pg_ctl ... start`, que el agente corre fuera del
sandbox, porque dentro no puede escribir su registro). Si `pg_ctl` dice que otro servidor puede estar en
ejecución, cerrar los procesos `postgres` colgados (el 2026-10-08 quedaron dos) y reintentar. Comprobar
también que no quede un escuchador viejo corriendo (`python -m leda escuchar`).

**Lo hecho en la sesión autónoma:** la regresión del motivo (funciona; `main` en `6ee287a`), la
conversación 26 (sin código) y la C-3 hasta la porción 4, revisada por commit (`odd/tasks/fase-c.md`).

**1. Lo primero de la próxima sesión: decisiones del usuario** (en `odd/tasks/fase-c.md`, `PENDIENTE`):
1. **Quién juzga lo que cubre un texto de la entrega** (hallazgo de la ronda con la IA real): hoy lo
   decide la IA y puede trabar la entrega. Opciones descritas en la bitácora ("La entrega y la aprobación
   con la IA real"); el ADR 0019 dice que la persona confirma o corrige.
2. **"¿Cuál de las dos?" se repite** cuando quien aprueba vuelve a mezclar aprobar y pedir cambios: qué
   pasa después de la única pregunta.
3. **El rato sin actividad** de la conversación 26 (propuesta: 5 minutos) y si la regla vale así.
4. **"La terminé" sobre una tarea que nunca arrancó:** ¿se anota el inicio y se entrega en el mismo
   mensaje? (hoy dice que no se puede).
5. **Una pieza retirada después de entregar** deja la evidencia incompleta y la tarea trabada en revisión.
6. **Si cambia quién aprueba** mientras el aviso espera, el nuevo no recibe nada.
7. **El tope diario:** los recordatorios a quien aprueba y el aviso de "trabada" a quien está arriba se
   contaron dentro del tope; "se destrabó", fuera. Confirmar.
8. **Los avisos de una decisión** (aprobada, cambios pedidos) salen sin el margen para corregir. Confirmar.
9. **Cómo probar el enlace a la página** por Telegram: hace falta `LEDA_BASE_URL` y que el servidor
   (`servir`) sea alcanzable desde el celular.

**2. Después:**
- **El comparador del corredor** marca como garantía una fila que sobra aunque sea lo confirmado, e
  imprime sólo las filas sin emparejar (`tests/conversaciones/comprobar.py`, `filas`): arreglarlo antes de
  la próxima ronda. Y aflojar en los YAML de la 21 a la 23 lo que la ficha permite (`puede_traer`).
- **La prueba por Telegram de la entrega y la aprobación**, con `leda_motor` puesto al día: aplicar las
  migraciones `0034` a `0037` y volver a importar el pack (las clases de cada tipo y los referentes de
  cada área), con respaldo previo y autorización del usuario.
- **Lo que queda de la C-3:** pedir el enlace por chat (una jugada nueva, con su conversación de prueba
  primero) y la porción 5, el acceso del administrador por el bot de administración.
- **Diez tablas con `workspace_id` sin `row level security`** (lista en `odd/tasks/fase-c.md`): ver si son sólo de administración o si les falta, contra la
  invariante de `AGENTS.md`.
- El resto de la Fase C (la persecución del bloqueo, las cadencias, delegar), que espera sus preguntas.

**Comandos de la prueba por Telegram** (`.venv\Scripts\python.exe -m …`, desde la carpeta del Motor):
- `leda escuchar corework`: el escuchador.
- `leda.motor.reloj corework adelantar|estado|volver`, y `hora HH:MM` para ir a una hora del mismo día. Entre
  salto y salto, esperar 2 minutos: los avisos se revisan una vez por minuto real.
- `leda chatgpt login|estado|salir` y `leda modelo gpt-6-sol --proveedor chatgpt`.
- `leda.motor.leer corework --completo`: el registro de turnos y los avisos guardados.
- **Ojo:** nunca correr el escuchador y una ronda del corredor a la vez, y nunca una ronda con la IA real
  mientras un escritor edita `src/` o `db/` en la misma carpeta (el 2026-10-07 una medición corrió con
  código a medio editar).

**`leda_motor`:** tiene los datos de la prueba del 2026-10-08 (tareas que vencen el viernes 16, semilla a 8
días) y el reloj de Leda puede haber quedado adelantado (`reloj corework volver`). Respaldo previo:
`db/respaldos/leda_motor-antes-motivo-20261008.dump`. Para una prueba nueva se recrea con respaldo previo
(autorización del usuario). El modelo activo es `chatgpt / gpt-6-sol`.

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
- **El archivo global `~/.claude/CLAUDE.md`:** unos 71.000 caracteres, lo maneja gentle-ai. El proyecto carga
  unos 78.400 (`LC_ALL=C.UTF-8 wc -m`, 2026-10-08): con el global, unos 149.700, al límite de 150.000.
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
| Rama del Motor | `pytest tests/garantias` | 2026-10-08 | 319 passed |

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
