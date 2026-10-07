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

## Punto exacto para retomar (2026-10-07, E3-8 medida; faltan dos decisiones del usuario y su prueba)

- **Qué:** el Motor, Etapa 3, con su plan en `odd/tasks/motor-definitivo.md`, aceptado el 2026-10-06.
  - **Hecha la Fase A** (E3-1 a E3-4): las garantías están en `tests/garantias/`, la entrada HTTP en
    `entrada.py`, y los flujos A y B y su banco, borrados. La migración `0032` borró las tablas del alta.
  - **Fase B:** el motor definitivo está en `src/leda/motor/` (E3-5 a E3-7), con la regla de hablar del
    mundo, y Leda vuelve a conversar: `python -m leda escuchar corework`.
  - **E3-8, hecho:** la regresión con GPT-6 sol (89 de 90, garantías 90 de 90) y la comparación de cinco IA
    (bitácora de flujos). Se queda sol.
  - **Decisiones del usuario para cerrar M3:**
    1. Las fechas a más de dos semanas: hecho; la lista se amplió a ocho semanas (2026-10-07). La regresión
       completa espera crédito en OpenRouter.
    2. `leda_motor` recreada (autorizado, 2026-10-07), con sol por la suscripción de ChatGPT del usuario: la
       regresión dio 90 de 90. Falta su prueba por Telegram, con la guía de `odd/tasks/motor-definitivo.md`,
       sección 4b.
  - Decisiones del usuario: los circuitos 5, 7, 8 y la persecución 3a, después de M3; la plataforma web,
    después de M3; no hay equipo real hasta que el usuario lo diga.
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
- **Respaldo de lo no subido.** `main` está subido hasta `e466eb5`, y la rama del Motor está subida. La rama
  congelada `feat/flujo-de-un-mensaje` (92 commits sin subir, 7 con líneas de atribución) y las etiquetas
  quedaron en un `git bundle` del repositorio entero (2026-10-07, verificado), sin reescribir nada:
  `D:\Proyectos\Leda-PM-respaldos\leda-repositorio-completo-20261007.bundle`. Está en el mismo disco:
  `PENDIENTE` copiarlo a la nube o a otro disco.
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
- **Producción:** cola de entrada, pool de conexiones, observabilidad, respaldo y restauración.
  - El webhook del motor (E3-7) ya tiene un secreto propio de cada bot.
  - Atiende un mensaje a la vez, bajo un candado global, y el candado de cada mensaje sigue tomado
    mientras responde la IA. Se resuelve con la cola de entrada, antes de usar Leda en un servidor
    (revisión de la E3-7).
- **Alta de un segundo cliente:** el proceso no está definido.
- **Autoridad sobre `cancelada`** (T2b): `PENDIENTE` de decisión.
- **Aviso por cambio de fecha** de dependencias sin disparador (la fecha comprometida es inmutable; su cambio va
  a la plataforma, ADR 0017, decisión 4).
- **Reintento del despachador:** puede reordenar partes de una respuesta partida.
- **ADR 0007:** dos puntos abiertos (respuesta sin opciones; opciones en el grupo de gestión).
- **Configuración:** el resumen "Estado del equipo" va a un grupo de Telegram que no existe (R4b-H7).
- **Tope de contacto por espacio y no por persona** (`docs/capacidades.md`, "Trampas conocidas").

`b-0005-b` (Jev con "el plc") quedó cerrada el 2026-10-06 por la medición de Jev (ADR 0018, decisión 7).
