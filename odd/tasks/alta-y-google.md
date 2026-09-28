# Alta con correo verificado y acceso a Google (rama auxiliar)

**Estado:** G0 cerrada (matriz aprobada, ADR 0010 aceptada, 2026-09-27) — próximo: G1
**Creado:** 2026-09-27
**Origen:** decisión del usuario, 2026-09-27; [`ADR 0010`](../../docs/decisions/0010-correo-verificado-y-google-en-el-producto.md).
**Rama/worktree:** `auxiliar/alta-y-google`, `D:\Proyectos\Prisma-PM-worktrees\alta-y-google`.

> **Para la sesión que trabaje esta rama:** este documento contiene todo lo que
> se decidió con el usuario antes de crearla. Esa conversación ocurrió en otra
> sesión, cuya memoria automática no está disponible acá (la memoria está atada
> a la carpeta del repositorio principal). No hace falta preguntarle al usuario
> qué hacer: está escrito abajo. Consultarlo sólo en los casos de
> "Cuándo consultar al usuario".

## Objetivo

Recuperar la verificación de correo en el alta (sumada al enlace de
activación existente) y construir el acceso a Google (Calendar, Gmail, Drive,
Docs) para agenda, reuniones y documentación — reproduciendo el
comportamiento aceptado que documenta el pack
`PRISMA-PACK-RECONSTRUCCION-20260925/`, sostenido por la arquitectura
multi-tenant vigente de este repositorio.

## Problema

`AGENTS.md` excluye hoy "agenda o calendarios externos" del producto sin una
decisión documentada; el alta sólo tiene enlace de Telegram; no existe ningún
código de Google en el repositorio. ADR 0010 abre el alcance; este documento
ordena y acota el trabajo.

## Decisiones del usuario ya tomadas (2026-09-27)

No volver a preguntarlas.

1. **El pack es trabajo propio del usuario.**
   `D:\Proyectos\PRISMA-PACK-RECONSTRUCCION-20260925\` documenta la
   implementación anterior de Prisma que el usuario construyó con otra IA. Lo
   que describe para alta, Google, agenda y reuniones **funcionaba bien y se
   quiere recuperar**. Para esta rama es la especificación de comportamiento
   (ver "Fuentes funcionales obligatorias").
2. **El alta con revisión administrativa y verificación de correo se
   replica.** Motivo: sin el correo de cada persona no se le pueden mandar
   las invitaciones y avisos de reuniones y eventos especiales por Calendar.
   Se suma al enlace de activación actual de `onboarding.py`, no lo
   reemplaza.
3. **Google, agenda y reuniones se construyen** ("si no hay nada en el repo,
   hay que hacerlo"). ADR 0010 es la decisión documentada que exige
   `AGENTS.md`.
4. **Esta rama es secundaria, auxiliar.** Mientras trabaja, `main` sigue como
   hasta ahora: alta por enlace de activación, sin correo ni Google. Recién
   cuando el usuario decida integrar, estas capacidades pasan a estar
   disponibles. La rama deja todo preparado para unirse a `main` y no toca
   nada que no le competa.
5. **Orden en `main`, para no depender de él:** la línea principal termina
   los seguimientos T6 de la entrega con evidencia y una tercera ronda por
   Telegram; después recupera el indicador de "escribiendo" (pack 05) y el
   saludo y tono (pack 06). Esas dos unidades **no** son de esta rama.

## Reglas de trabajo (las mismas que en la sesión principal)

- **Nunca fallar en silencio.** Toda falla al procesar un mensaje, un toque
  o un efecto externo registra un incidente saneado (sin cuerpos de mensaje
  ni secretos) y deja a la persona un aviso neutral ("No pude completar eso.
  Ya quedó registrado para revisarlo."). Nunca responder "no se aplicó ningún
  cambio" sin saberlo. Al diseñar un handler, escribir primero el camino de
  falla.
- **Ninguna protección se degrada en silencio.** Si falta o falla algo que
  protege la interpretación o un efecto (la credencial de Google, la
  verificación, la vista previa), Prisma actúa como en duda: pregunta o no
  aplica nada, y lo deja visible con un incidente. Nunca un "si no hay clave,
  seguimos sin eso". Las pruebas inyectan dobles explícitos.
- **Prisma ayuda, no fastidia.** Preferir el flujo con menos pasos, menos
  preguntas y textos más cortos, siempre que se mantengan los invariantes
  (hechos distintos son registros distintos, no acciones distintas de la
  persona). Firme donde importa: seguir lo atrasado y lo que no tiene
  respuesta.
- **Autonomía en commits y revisión.** Hacer los commits de cada unidad de
  trabajo y correr la evaluación de RDD sin pedir permiso. El sobre de
  consentimiento de cada revisión sí lo contesta el usuario, siempre
  transmitido completo.
- **Una pregunta por vez, y sólo cuando es de verdad del usuario.**
- Lo que manda `AGENTS.md` sigue valiendo entero: no leer `.env*`, no
  ejecutar `python -m prisma esquema --recrear`, no correr SQL destructivo ni
  pruebas contra una base no descartable, no registrar cuerpos de
  conversación en documentación.

## Cuándo consultar al usuario (lista cerrada)

Sólo en estos casos. Todo lo demás se resuelve sin preguntar.

1. **G0:** aprobar la matriz de capacidades, contratos, permisos y validación,
   y aceptar ADR 0010.
2. **Las seis decisiones abiertas de ADR 0010**, de a una, cuando la rebanada
   que las necesita esté por empezar (modelo de OAuth, scopes iniciales,
   Gmail en la primera tanda, dónde vive el consentimiento OAuth, dónde vive
   la revisión administrativa, cifrado de credenciales).
3. **Cualquier conflicto entre el pack y el repositorio** (ver "Regla de
   precedencia").
4. **Un ítem D o P del pack** que se quiera tratar como comportamiento
   aceptado.
5. **Lo que requiere al usuario físicamente:** proyecto de Google Cloud,
   pantalla de consentimiento OAuth, cuentas reales de Google con datos
   ficticios, copiar `.env.test` al worktree, sesiones reales por Telegram.
6. **El sobre de consentimiento de cada revisión de RDD.**
7. **Cualquier cosa que toque `main`:** rebase conflictivo sobre archivos de
   la línea principal, push, integración.
8. **Un cambio de alcance** respecto de este documento o de ADR 0010.

## Alcance

**Incluido:** verificación de correo añadida al alta; almacenamiento de
credencial de Google por espacio; lectura de Calendar; creación/modificación
de eventos con vista previa y confirmación; reuniones y minutas apoyadas en
evidencia/aprobación; Gmail/Drive/Docs según se decida en G6.

**Excluido:** todo lo que ADR 0010 lista en "Qué queda fuera de esta
decisión" (Sheets/Contacts/Meet/Slides, grabación/transcripción automática,
correo a externos, la verificación por respuesta de correo como mecanismo
primario, aplicación móvil, cualquier cambio a `nucleo/`), más el saludo
diario y el indicador de Telegram (unidades de `main`).

## Fuentes funcionales obligatorias

El pack `PRISMA-PACK-RECONSTRUCCION-20260925/` es la **especificación del
comportamiento a reproducir**: describe el qué (flujos, estados, mensajes
exactos, reglas, la experiencia ya aceptada). No es antecedente a ignorar ni
una sugerencia: es la referencia contra la que esta unidad se mide. Leer en
este orden, completo, antes de G0:

| Archivo (relativo a `D:\Proyectos\PRISMA-PACK-RECONSTRUCCION-20260925\`) | Gobierna |
|---|---|
| `00-LEER-PRIMERO.md` | Cómo interpretar V/I/D/P; reglas transversales 1-10; instrucción para la IA receptora (matriz de G0) |
| `01-INCORPORACION-E-IDENTIDAD.md` | Recorrido completo de alta con correo (G1) |
| `02-GOOGLE-ACCESO-Y-OPERACIONES.md` | Acceso a Google, permisos, contrato de propuesta, estados y concurrencia (G2, G4, G6) |
| `03-REUNIONES-EVENTOS-Y-AGENDA.md` | Agenda, eventos, reuniones y minutas (G3, G4, G5) |
| `VALIDACION-PARA-LA-NUEVA-IMPLEMENTACION.md` | Batería de aceptación (Tanda 1 human-first, Tanda 2 Telegram real); casos mapeados por rebanada abajo |
| `FUENTES-Y-TRAZABILIDAD.md` | Qué evidencia respalda cada afirmación de 01-03; límites de cada fuente |
| `anexos/LEER-CODIGO.md` | Cómo usar los extractos de código; qué es adaptación nueva y qué original |
| `anexos/EXTRACTOS-VERIFICADOS.json` | Rangos y huellas exactas de cada extracto citado |

Anexos de código de esta unidad (bajo `anexos/codigo/`, todos de
`01-INCORPORACION-E-IDENTIDAD.md`; no hay extractos de código para Google: 02
y 03 son doctrina y diseño):

`incorporacion-can_resend.py.txt`, `incorporacion-claim_verification_token.py.txt`,
`incorporacion-email_prompt_message.py.txt`, `incorporacion-receive_email.py.txt`,
`incorporacion-welcome_message.py.txt`; y, sólo como contexto de que la
bienvenida cuenta como saludo del día, `incorporacion-claim_greeting.py.txt`,
`incorporacion-complete_greeting_claim.py.txt`,
`incorporacion-greeting_for.py.txt`,
`incorporacion-make_daily_greeting_hooks.py.txt`. **El saludo diario no se
construye en esta rama** (es la unidad del pack 06 en `main`): G1 deja
registrado el hecho de la bienvenida de forma que esa unidad pueda contarlo
después, y anota la dependencia en "Progreso".

**Fuera de alcance, no usar:** `indicador-*`, `telegram-*` y `prueba-*`
(packs 05/06, unidades de `main`).

### Regla de precedencia (obligatoria)

El pack define el **qué**: flujos, estados, mensajes exactos, reglas, la
experiencia ya aceptada. El corpus de este repositorio define el **cómo**:
aislamiento multi-tenant por RLS, `docs/architecture/frontera.md`, `nucleo/`,
vista previa/confirmación/ejecución única/auditoría, `message_outbox`,
PostgreSQL como fuente de verdad. Ante un conflicto, **no elegir en
silencio**: registrarlo como `PENDIENTE` en "Conflictos qué/cómo" (abajo) y
preguntarle al usuario antes de seguir con esa rebanada. Las etiquetas
V/I/D/P se conservan: un ítem D o P no es comportamiento probado para copiar
a ciegas; necesita la confirmación del usuario o su propia validación.

### Conflictos qué/cómo

Semilla identificada al redactar este documento; agregar los que aparezcan.

- `01-INCORPORACION-E-IDENTIDAD.md` §4 describe los cinco estados como un
  campo; la regla 4 de `frontera.md` exige proyección por eventos. G1 lo
  resuelve en la forma, sin cambiar ningún estado ni mensaje visible de §5.
  (No requiere consulta: es sólo el cómo.)
- `02-GOOGLE-ACCESO-Y-OPERACIONES.md` §5 propone una operación genérica
  `workspace_mutate`; este repositorio usa una herramienta por acción
  (`herramientas.REGISTRO`). `PENDIENTE` de confirmación en G0 (ADR 0010,
  alternativas).
- `01-INCORPORACION-E-IDENTIDAD.md` §3.3 asume una superficie protegida de
  revisión administrativa que hoy no existe. `PENDIENTE`: decisión abierta 5
  de ADR 0010.
- `02-GOOGLE-ACCESO-Y-OPERACIONES.md` §7 exige un estado durable "en
  ejecución" antes de llamar a Google; `pending_action`/`Preparacion` no lo
  tienen porque sus efectos son atómicos en PostgreSQL. G4 lo diseña
  explícitamente y presenta el diseño al usuario antes de construirlo.

### Rebanadas y qué reproducen

| Rebanada | Secciones del pack que replica | Anexos de código | Casos de `VALIDACION` |
|---|---|---|---|
| G0 | `00-LEER-PRIMERO.md`, "Instrucción breve para la IA receptora" | — | ninguno propio (gate previo a Tanda 1) |
| G1 | `01-INCORPORACION-E-IDENTIDAD.md` completo (§1-9) | los `incorporacion-*` de alta y correo | A01-A05; X01, X02 |
| G2 | `02-GOOGLE-ACCESO-Y-OPERACIONES.md` §2, §3, §6; W02 | ninguno | ninguno propio (base de G3-G6) |
| G3 | `03-REUNIONES-EVENTOS-Y-AGENDA.md` §3; `02-...` §4 (Calendar), §9 | ninguno | plantilla de G01 aplicada a lectura de agenda |
| G4 | `03-...` §2, §4; `02-...` §6, §7 | ninguno | C01-C03; G02-G04 |
| G5 | `03-...` §1, §5, §6, §7 | ninguno | S01 (avance vs. cierre); X01, X02 |
| G6 | `02-...` §4 (Gmail/Drive/Docs), §8, §10 | ninguno | G01-G04; X02 |

`S02-S05` (seguimiento/silencio), `U01-U03` y `H01-H03` (indicador y saludo)
pertenecen a unidades de `main`; no se usan acá.

## Contrato de rama auxiliar

- **Secundaria.** `main` tiene prioridad. Rebasar sobre `main` seguido — como
  mínimo antes de cada rebanada y antes de proponer integración. Esta rama
  nunca hace push a `main` ni se integra sola; la integración es decisión del
  usuario y la hace la sesión principal.
- **Rangos reservados:** migraciones `0100`-`0199` (`main` sigue usando
  `0015` en adelante, por debajo de `0100`). Antes de cada migración nueva,
  rebasar y confirmar que `main` no se acercó a `0100`. Números de ADR
  posteriores a `0010` quedan para `main`: si esta rama necesita una decisión
  propia, la registra como `docs/decisions/01xx-<slug>.md` (mismo rango que
  sus migraciones) y se renumera al integrar. Al integrar, esta rama renumera
  lo suyo, nunca lo de `main`.
- **Archivos propios** (los crea; nadie más los toca): `src/prisma/google/`
  (`__init__.py`, `credenciales.py`, `calendario_externo.py` — nombre
  distinto de `src/prisma/calendario.py`, que es el calendario *laboral* y no
  se toca —, `correo.py`, `documentos.py`), `src/prisma/alta_correo.py`
  (paralelo a `onboarding.py`), `tests/test_alta_correo.py`,
  `tests/test_google_credenciales.py`, `tests/test_agenda_google.py` y demás
  pruebas nuevas, escenarios de banco propios con prefijo `g-`,
  `db/migrations/01xx_*.sql` y `db/rollbacks/01xx_*.sql`, este documento y
  su espejo en Engram.
- **Archivos compartidos** que puede tocar mínimamente, listando cada toque
  en el mensaje del commit: `db/esquema.sql` (sólo agregar),
  `src/prisma/herramientas.py` (registrar herramientas nuevas en
  `REGISTRO`, nunca cambiar las existentes), `src/prisma/autoridad.py`
  (acciones nuevas), `src/prisma/gateway.py` (extender `_activacion`/webhook
  con casos propios), `src/prisma/onboarding.py` (sumar, nunca reemplazar;
  sin cambiar la firma de `activar()`/`generar_enlaces()`),
  `src/prisma/cli.py` (comandos nuevos), `docs/architecture/frontera.md`
  (agregar el puerto de la decisión 7 de ADR 0010), y ADR 0010 (sólo su
  estado al aceptarse en G0).
- **Archivos que NO debe tocar:** `nucleo/`; `AGENTS.md` y `CLAUDE.md` (los
  actualiza la sesión principal al aceptarse ADR 0010); `docs/STATUS.md`;
  `docs/ROADMAP.md`; `docs/capacidades.md`; `odd/tasks/prisma-orienta.md`;
  el área T6 de `src/prisma/herramientas.py` y `src/prisma/menu_tarea.py`
  (entrega con evidencia, "Pedir cambios", en curso en `main`); los
  escenarios existentes de `tests/banco/` y su corredor.

### Preparación para integrar

- [ ] Todo lo nuevo apagado por defecto por espacio: claves de
  `workspace_setting` `google.habilitado` y `correo_verificacion.habilitado`
  en `false` hasta activación explícita. El merge no cambia ningún
  comportamiento de `main`.
- [ ] Cada migración `01xx` tiene su rollback y pasa el ensayo de paridad de
  `tests/test_task_intake.py`
  (`test_los_rollbacks_devuelven_la_base_al_estado_anterior`,
  `test_migration_clean_schema_parity_and_guarded_rollback`), que descubre
  las migraciones solo.
- [ ] Suite completa verde sobre la rama rebasada contra `main`.
- [ ] `tests/test_capacidades.py` en verde (esquema nuevo con uso declarado,
  `test_no_hay_esquema_nuevo_sin_uso_ni_declarado`).
- [ ] Ningún archivo de "NO debe tocar" aparece en el diff contra `main`.
- [ ] Checklist de integración revisado con el usuario.

## Preparación del entorno del worktree

Un worktree nuevo no trae lo que no se versiona.

1. **Entorno de Python:** crear `.venv` en el worktree e instalar el proyecto
   con sus extras de desarrollo (`pyproject.toml`).
2. **`.env.test`:** lo copia el usuario desde el repositorio principal. La
   sesión nunca lo lee ni lo imprime. Cada corrida de la suite crea su propia
   base con nombre irrepetible y la borra al terminar (`tests/conftest.py`),
   así que puede correr en paralelo con la suite de `main` contra el mismo
   servidor.
3. **CodeGraph:** este worktree necesita su propio índice
   (`gentle-ai codegraph init --cwd <worktree>`); nunca copiar el de otra
   carpeta.
4. **Engram:** el proyecto es el mismo (`prisma-pm`). Usar temas con prefijo
   `odd/alta-y-google/` para no pisar los de `main`.

## Tareas

- [x] **G0 — Matriz de aceptación y OK del usuario.** Antes de escribir
  código: presentar la matriz que exige `00-LEER-PRIMERO.md` ("Instrucción
  breve para la IA receptora"): capacidades y estados, contratos, permisos y
  plan de validación, para G1 a G6, con el mapa de casos de `VALIDACION`.
  Obtener la aprobación explícita del usuario y la aceptación de ADR 0010
  (pasa de `propuesta` a `aceptada`). Confirmar ahí el conflicto
  `workspace_mutate` frente a herramientas discretas. Sin las dos
  aprobaciones, no se abre G1.
- [ ] **G1 — Correo verificado en el alta.** Recorrido de
  `01-INCORPORACION-E-IDENTIDAD.md` §3, sumado a `activation_token`; estados
  de §4 como proyección por eventos; mensajes exactos de §5; controles de §6
  (vigencia, reserva, hash, límites de reenvío); recuperación administrativa
  de §8 sobre la superficie que resuelva la decisión abierta 5. Criterio de
  cierre: con la clave apagada, activar por Telegram funciona exactamente
  igual que hoy; encendida, el correo se pide, se verifica y queda registrado
  como hecho auditable aparte.
  - [x] **G1a — Esquema del alta con correo.** Migración `0100` + rollback:
    eventos de alta append-only con proyección por disparador (estados de
    §4, `review_required`, modo `alta`/`existente`); token de verificación
    sin privilegios de `prisma_app` y funciones `security definer` de
    `prisma_owner` (emitir, reservar 5 min, consumir, vencer 24 h, límites
    3/h y 5/ciclo); contacto verificado por integrante con alta idempotente
    por función; avisos administrativos persistentes (leído ≠ resuelto).
    Todo con `workspace_id`, RLS forzada y `aislamiento_espacio`. Pruebas:
    transiciones válidas e inválidas, aislamiento entre espacios,
    `prisma_app` sin acceso directo, paridad migración/rollback,
    `test_capacidades`.
    Hecho (ruta: delegada, un escritor; disparador: esquema, migración,
    rollback, capa Python y pruebas). Tablas `alta_correo_evento` (append-only)
    + proyección `alta_correo_estado` con grafo validado en la base,
    `alta_correo_contacto`, `alta_correo_verificacion` (sólo por funciones,
    como `acceso_tablero`), `aviso_administrativo`. Seguimiento para G1d:
    hoy `prisma_app` tiene `update` directo sobre `aviso_administrativo`;
    marcar leído/resuelto debe quedar sólo para el canal de administración.
    Revisión RDD `review-d95ced9967467a93` (riesgo medio, consentida por el
    usuario, lente de confiabilidad): un hallazgo CRITICAL
    (`completar_verificacion_correo` escribía el contacto antes de validar el
    estado) corregido en `7a21374` con prueba nueva (RED observado → GREEN;
    suite completa `993 passed, 108 deselected`); validación dirigida
    aprobada; reconocimiento emitido (autoridad consumida).
  - [x] **G1a2 — Endurecimiento tras la revisión** (hallazgos no bloqueantes
    de la misma revisión): `emitir_verificacion_correo` bloquea la
    proyección y exige `awaiting_email` o `pending_email_verification`
    (límites 3/h y 5/ciclo sin carrera; la carrera sobre el índice único
    devuelve un motivo tipado, no una excepción); `completar` fija el espacio
    del token antes de tocar tablas con RLS; pruebas de los caminos de falla
    de `completar` (`verification_state_changed`, `email_in_use` tras la
    reserva, `verification_token_busy` sin reserva o vencida) verificando que
    no queda contacto y que la reserva se libera; `habilitado()` filtra por
    el espacio; `prisma_app` sin `update` directo sobre
    `aviso_administrativo` si G1d no lo necesita.
    Hecho (ruta: delegada, un escritor). Motivos nuevos
    `verification_state_invalid` y `verification_conflict`; prueba real de
    concurrencia con dos conexiones (RED: `UniqueViolation` sin capturar →
    GREEN); `reservar`/`completar` funcionan sin espacio declarado (RED:
    `verification_token_invalid` → GREEN); `habilitado(cur, workspace_id)`
    filtra por espacio. Los tres caminos de falla de `completar` resultaron
    guardas de regresión (ya correctos). El `update` de `prisma_app` sobre
    `aviso_administrativo` queda para G1d. Suite: `1000 passed, 108
    deselected`; repetición parcial de la sesión: `133 passed`.
    Revisión RDD `review-36cb59bfd957a460` (riesgo medio, consentida):
    aprobada sin correcciones; reconocimiento emitido. Advertencia aplicada:
    la prueba de concurrencia ya no puede colgarse (barrera y `join` con
    tiempo de espera). Sugerencia pendiente, menor: ninguna prueba alcanza
    la rama defensiva `verification_conflict` (el bloqueo la vuelve
    inalcanzable en la práctica).
  - [x] **G1b — Recorrido del alta con correo.** `alta_correo.py` con puerto
    de envío (`Protocol`) y doble de prueba; sin emisor configurado con la
    clave encendida → incidente + aviso neutral, nunca "enviado".
    Bienvenida y pedido de correo del pack al activar (clave encendida);
    recepción del correo, envío, `/start pv_{token}` en
    `gateway._activacion`, reenviar/cambiar, mensajes literales de §5,
    control antes del despacho conversacional para el modo `alta`.
    Hecho (ruta: delegada, un escritor; `alta_correo_flujo.py` nuevo;
    toques compartidos: `gateway.py` — `_bot_username`, `/start pv_`,
    compuerta previa al agente, botones en `_toque` —, esquema y migración
    0100 — función `verificacion_vigente_correo` —, rollback 0100). TDD: el
    escritor declaró que no escribió todas las pruebas antes del código;
    hubo RED reales (transición faltante, RLS bajo `admin()`, orden del
    outbox) antes del GREEN. La sesión corrigió dos defectos antes del
    commit, con RED observado: el error de `getMe` filtraba el token del bot
    a `incident.referencia_cruda` (ahora error saneado), y el texto de
    límite agotado decía "Le avisé a administración" cuando el aviso todavía
    no se entrega (G1d) — ahora "Quedó registrado para que administración te
    ayude". `nombre_preferido` = primera palabra del nombre guardado (igual
    que `onboarding.bienvenida`). Textos nuevos fuera del pack: pendientes
    de revisión del usuario. Suite: `1047 passed, 108 deselected`.
    Revisión RDD `review-bf8c04f01554e3f3` (riesgo medio, consentida):
    aprobada; reconocimiento emitido. Advertencias no bloqueantes → G1b2.
  - [x] **G1b2 — Endurecimiento tras la revisión de G1b.** (1) La compuerta
    sólo actúa en chat privado: en un grupo nunca se piden, muestran ni
    procesan correos. (2) "Cambiar correo a X" no deja el ciclo en
    `awaiting_email` si la emisión o el envío fallan (todo dentro del mismo
    savepoint). (3) Cada botón relee el estado del ciclo antes de actuar; un
    botón viejo no emite ni transiciona fuera de su estado. (4) Dentro del
    savepoint, la transición antes del envío: el envío es el último efecto.
    (5) Pruebas faltantes: recuperación desde `pending_welcome` sin
    duplicados, límite de 5 envíos con su aviso administrativo, nombre
    vacío sin `IndexError`.
    Hecho (ruta: delegada, un escritor; RED de todo el lote antes de los
    arreglos: `13 failed, 2 passed`). En un grupo, el mensaje de un
    integrante con el alta pendiente no se procesa ni se responde (no es una
    falla: el pedido de correo va por privado). Textos nuevos sólo para
    nombre vacío (bienvenida, ✅ y correo sin nombre), pendientes de revisión
    junto con los demás. Toque compartido: `gateway.procesar_update`
    (compuerta sólo en privado; bloqueo en grupo). Suite: `1062 passed, 108
    deselected`; repetición de la sesión: `96 passed` en las pruebas del
    alta con correo.
    Revisión RDD `review-e40fae6aa783e90f` (riesgo medio, consentida):
    aprobada; reconocimiento emitido. Seguimientos no bloqueantes: (a) dos
    mensajes simultáneos en `pending_welcome` pueden chocar contra el índice
    único de la bienvenida (termina en incidente + aviso neutral, no en datos
    corruptos) → bloquear la proyección al completar; (b) el aviso
    `correo_limite_agotado` "una sola vez" no resiste concurrencia → índice
    único parcial en `aviso_administrativo`. Ambos entran en G1d, que ya
    toca esa tabla.
  - [x] **G1c — Integrantes ya activos (modo `existente`).** Al encender la
    clave (comando de `cli.py`), a quien ya estaba activo sin correo se le
    pide una vez, sin bloquearlo; en ese modo sólo un mensaje que es
    exactamente una dirección de correo entra al recorrido, el resto va al
    agente como siempre.
    Hecho (ruta: delegada, un escritor). Comando `correo-verificacion
    <espacio> --activar|--desactivar` (toque compartido: `cli.py`, comando
    nuevo; `gateway.procesar_update`, derivación a `atender_existente` en
    privado). Corrigió un defecto real con RED observado: con la clave
    apagada, un integrante a mitad del ciclo `alta` seguía bloqueado
    (`gate` y `bloqueada_para_negocio` no miraban la clave). El resto de las
    pruebas se escribió junto con el código, no antes (desvío de TDD
    declarado por el escritor). Texto nuevo pendiente de revisión:
    "✅ Gracias, {nombre}. Tu correo quedó verificado." (y sin nombre).
    Suite de la sesión: `1 failed, 1075 passed, 108 deselected`; la falla
    (`test_0008_motivo_no_arranca_tarea_llega_por_migracion`) y las dos que
    vio el escritor son pruebas de migración ajenas a esta unidad que
    fallaron con `tuple concurrently updated` y pasan aisladas
    (`5 passed`): contención de catálogo con otra suite corriendo contra el
    mismo servidor. `PENDIENTE`: confirmar con una corrida sin concurrencia.
    Revisión RDD `review-7c6ef19f12bf541c` (riesgo alto por `cli.py`,
    consentida; cuatro lentes): aprobada; reconocimiento emitido.
  - [x] **G1c2 — Endurecimiento tras la revisión de G1c.** (1) La clave de
    deduplicación del pedido de correo incluye el ciclo: un ciclo reabierto
    tras revocar sin verificar vuelve a recibir el pedido (hoy quedaría
    deduplicado y nunca saldría). (2) "Exactamente una dirección" estricto:
    rechaza URLs con `@`, `usuario@host:ruta`, dos `@` y puntuación final.
    (3) Pruebas faltantes: `pending_email_verification` en modo `existente`
    (misma dirección → al agente, sin recordatorio; distinta → propuesta de
    cambio); con la clave apagada, un integrante a mitad del `alta` deja de
    ser bloqueado también en grupo; reapertura de un ciclo revocado sin
    contacto. (4) La consulta de elegibilidad de `--activar` filtra por
    `workspace_id` explícito y toma un bloqueo para corridas superpuestas.
    (5) Legibilidad: un solo conjunto de estados abiertos compartido, el
    comentario de `gateway` corregido, fixtures compartidas en un módulo
    común.
    Hecho (ruta: delegada, un escritor; TDD con RED por ítem). RED
    observados: el pedido del ciclo 2 quedaba deduplicado (1 en vez de 2);
    las cuatro formas laxas entraban al recorrido; faltaba
    `elegibles_existente`. Las pruebas del punto 3 son guardas de regresión
    (el código ya era correcto). Un punto final después de la dirección se
    rechaza (va al agente). Toques compartidos: `cli.py` (consulta con
    `workspace_id` explícito + bloqueo consultivo por espacio), `gateway.py`
    (sólo comentario). Suite del escritor: `1087 passed, 108 deselected`;
    repetición de la sesión: `121 passed` en las pruebas del alta con correo.
    Revisión RDD `review-33cd2defb2564552` (riesgo alto por `cli.py`,
    consentida; cuatro lentes): aprobada; reconocimiento emitido.
    Seguimientos no bloqueantes que entran en G1d: la prueba del bloqueo
    consultivo tiene que comprobar que la corrida en segundo plano terminó
    bien (código 0, ciclos abiertos); la prueba de filtro por espacio tiene
    que probar filas de otro espacio con resultado no vacío; la parte local
    estricta rechaza puntos al inicio, al final y consecutivos; docstring
    confuso sobre URL; chequeo redundante de vacío.
  - [x] **G1d-a — Entrega de avisos por el bot de administración.** Hecho
    (ruta: delegada, un escritor). `avisos_admin.py`: entrega por
    administrador (`aviso_administrativo_entrega`), reintentos e incidente,
    botón **Marcar leído** (rol revalidado), texto libre → guía sin acción;
    enganchado al mismo ciclo que despacha el outbox (`local.py`, `cli.py
    despachar`). Aviso único por referencia (índice parcial), bienvenida con
    candado, parte local estricta sin puntos inválidos, pruebas de la
    revisión de G1c2 mejoradas. El escritor declaró que la entrega y el
    webhook no se hicieron con prueba primero. Toques compartidos:
    `gateway.py` (rama de administración), `local.py`, `cli.py`,
    `tests/conftest.py` (truncado de `aviso_administrativo_respuesta`),
    esquema/migración/rollback 0100. La sesión corrigió antes del commit una
    regresión de privilegios con RED observado: el escritor había dado
    `update` sobre `alta_correo_estado` a `prisma_app` para tomar un
    candado, y con eso `prisma_app` podía fijar la marca de sesión y
    escribir `active` sin verificar; ahora el candado se toma con
    `bloquear_alta_correo_estado()` (`security definer`, `prisma_owner`) y
    `prisma_app` vuelve a sólo `select`. Suite de la sesión: `2 failed,
    1172 passed, 108 deselected`; las dos fallas son pruebas de migración de
    `test_task_intake.py` que pasan aisladas (`4 passed`), el mismo patrón
    de contención ya registrado.
    Revisión RDD `review-32981fbfd82ee215` (riesgo alto, consentida; cuatro
    lentes): aprobada; reconocimiento emitido.
  - [x] **G1d-a2 — Endurecimiento tras la revisión de G1d-a.** (1) El
    despacho de avisos en `local.py` queda contenido (try/rollback +
    incidente): un error de administración nunca frena el despacho de un
    espacio. (2) Reintentos con espera creciente real (columna de próximo
    intento), no en cada pasada. (3) La reconciliación de entregas no
    recorre toda la historia en cada pasada: sólo avisos no resueltos (un
    administrador nuevo no recibe avisos ya resueltos) y acotada. (4) El
    incidente "falta token / no hay administrador" se deduplica sólo
    mientras el anterior sigue abierto: si el problema vuelve, vuelve a
    quedar registrado (nunca fallar en silencio). (5) El índice único de
    avisos incluye `workspace_id`, y el respaldo de `crear_aviso` nunca
    devuelve `None`. (6) El candado de la bienvenida también serializa
    cuando la fila todavía no existe o la sesión no declaró espacio. (7)
    Legibilidad: comentario de `verificacion_vigente_correo` en su lugar,
    retorno muerto de `_fallo` y conteo de `fallidos`, anotación
    `Transporte | None`, `rollback` con conexión nula en las pruebas.
    Hecho (ruta: delegada, un escritor). Despacho administrativo contenido
    en `local.py`/`cli.py`; `proximo_intento_en` con espera `2**(n-1)`
    minutos; reconciliación en una sola sentencia sobre avisos no
    resueltos; incidentes de plataforma deduplicados en una ventana de 24 h
    (la tabla `incident` no tiene estado de resolución) con bloqueo
    consultivo; `workspace_id` en el índice único de avisos;
    `bloquear_alta_correo_estado` pasa a bloqueo consultivo por membresía
    (sirve sin fila y sin espacio declarado). TDD débil declarado por el
    escritor en varios ítems (pruebas en verde al primer intento, RED
    razonado sobre el código anterior). Sin cambios de permisos ni RLS
    (verificado sobre el diff). Pruebas del alta con correo, avisos,
    migraciones y capacidades: `241 passed`. Suite completa del escritor:
    `7 failed, 1175 passed`: 3 de migración por contención (pasan aisladas)
    y 4 de `tests/test_aprobacion_cierra_tarea.py`, que fallan igual sin
    esta unidad: la prueba de `main` usa `AHORA = datetime(2026, 9, 27,
    ...)` fijo y desde el 2026-09-28 la acción pendiente figura vencida.
    Hallazgo para `main`.
    Revisión RDD `review-6e2a912d445df569` (riesgo alto, consentida; cuatro
    lentes): aprobada; reconocimiento emitido.
  - [x] **G1d-a3 — Correcciones tras la revisión de G1d-a2.** (1)
    Regresión: `abrir_ciclo_alta` ya no abre un ciclo nuevo si existe una
    proyección de un ciclo anterior (p. ej. reactivación tras `revoked`);
    debe abrirlo, sin perder la protección contra la carrera de la primera
    activación. (2) La contención del despacho administrativo en `local.py`
    registra un incidente en cada pasada si el error persiste: deduplicar
    con la misma ventana que los incidentes de plataforma. (3) Una sola
    definición de "administrador con Telegram" para despachar y reconciliar.
    (4) Prueba de la contención en `cli.py despachar` (lo del espacio que ya
    se despachó sobrevive). (5) Docstrings de
    `_incidente_plataforma_persistente` y `crear_aviso` fieles al código;
    constante con nombre para los reintentos de `crear_aviso`; claves de
    bloqueo consultivo con espacio de nombres propio para no chocar entre
    sí. Nota: la migración `0100` se edita en su lugar porque nunca se
    aplicó en ninguna base; si llegara a aplicarse antes de integrar, los
    cambios siguientes irían en una migración nueva `01xx`.
    Hecho (ruta: delegada, un escritor). RED observados en los ítems 1, 2 y
    4. Además de lo pedido corrigió dos fallas silenciosas reales: las
    claves de deduplicación de la bienvenida y el pedido no incluían el
    ciclo (un ciclo reabierto nunca los habría enviado), y `cli.py
    despachar` no confirmaba entre el despacho del espacio y el
    administrativo, por lo que el incidente de plataforma quedaba etiquetado
    con un espacio. Ítem 3 con guardas de regresión; ítem 5 sin prueba
    propia (documentación y espacios de nombres de bloqueos). Toques
    compartidos: `local.py`, `cli.py`, esquema/migración 0100 (sólo la clave
    del bloqueo). Sin cambios de permisos ni RLS (verificado sobre el diff).
    Repetición de la sesión: `247 passed`. Suite completa del escritor:
    `1182 passed, 6 failed` (las 4 de fecha fija de `main` y 2 de migración
    por contención, que pasan aisladas).
    Revisión RDD `review-b80bd0e2a9b99326` (riesgo alto, consentida; cuatro
    lentes): aprobada, sólo advertencias menores; reconocimiento emitido.
    Pasan a G1d-b: si falla también el registro del incidente,
    `reportar_fallo_despacho` no deja rastro (debe escribir a stderr y
    `cli.py` no debe decir "quedó registrado"); docstrings inexactos
    (conexión, `hashtext`, columna `etapa`); prueba del camino de doble falla.
  - [x] **G1d-b + G1t — Acción "Habilitar un nuevo intento" y textos
    aprobados.** Aplicar la sección "Textos del alta con correo aprobados
    por el usuario" (regla sin callejones sin salida, B1-B12, C, sin
    variantes sin nombre) y la acción F del administrador.
    Hecho (ruta: delegada, un escritor). Textos B1-B12, C y F aplicados
    literalmente; sin variantes sin nombre (un nombre vacío es un error de
    datos → incidente + aviso neutral); evento `intento_habilitado` que
    reinicia el tope de 5 por ciclo; funciones `existe_verificacion_correo`
    (sólo booleano) y `proximo_reenvio_correo` (hora de B11). El escritor
    declaró pruebas después del código para la reescritura de B1-B12. La
    sesión corrigió antes del commit, con RED observado: (a) si a la persona
    no se la podía avisar, el aviso quedaba resuelto y el administrador
    recibía "Listo, habilitado." — ahora no se aplica nada, queda un
    incidente y el administrador recibe el aviso neutral; (b) dos
    administradores confirmando a la vez aplicaban dos veces — ahora el
    aviso se bloquea al confirmar. Cambios de permisos, justificados:
    `prisma_owner` lee `alta_correo_evento` (para contar desde el último
    `intento_habilitado`), `prisma_admin` ejecuta
    `verificacion_vigente_correo`, y las dos funciones nuevas sólo para
    `prisma_app`. Suite de la sesión: `4 failed, 1210 passed, 108
    deselected` (las 4 de fecha fija de `main`). Textos nuevos del bot de administración:
    la vista previa del administrador ("¿Habilitar un nuevo intento de
    verificación de correo para {nombre}? Le vuelvo a preguntar por su
    correo y este aviso queda resuelto."), "Ese aviso ya estaba resuelto.",
    "Listo, habilitado.", "No se habilitó nada." — aprobados por el usuario
    (2026-09-28). El evento del
    administrador se registra con `actor_kind = 'persona'` (el enum
    `tipo_actor` de `main` no tiene `administrador`).
- Requisito de la Tanda 2 cumplido por el usuario (2026-09-28): el token del
  bot de administración está en `.env` del worktree
  (`PRISMA_BOT_TOKEN_ADMIN`; el archivo existe y git lo ignora; la sesión no
  lo leyó).
    Revisión RDD `review-c73c0f22b0e0ce26` (riesgo alto, consentida; cuatro
    lentes): aprobada; reconocimiento emitido.
  - [x] **G1d-b2 — Correcciones tras la revisión de G1d-b.** (1) El cuerpo
    del correo de verificación quedó con cortes de línea y sangrías copiados
    del documento: debe ser el texto A en párrafos corridos (sólo los saltos
    de párrafo aprobados). (2) Un enlace consumido de un ciclo anterior no
    puede decir "Tu correo ya está verificado ✅" si el ciclo actual no lo
    está: responder según el estado actual (B9). (3) "Habilitar un nuevo
    intento" comprueba el estado del ciclo (sólo `pending_email_verification`
    con el límite agotado); si no corresponde, no aplica nada y lo dice. (4)
    Nunca "??:??" en B11: si no se puede calcular la hora, incidente + aviso
    neutral. (5) Ningún texto alcanzable termina en "escribime y lo vemos" o
    "pedime que te lo reenvíe" (`TEXTO_ESTADO_CAMBIO`,
    `TEXTO_ENLACE_INVALIDO`): reemplazarlos por el paso siguiente según el
    estado. (6) Las respuestas del bot de administración no se pierden por
    deduplicación (Cancelar dos veces, dos administradores). (7) Una sola
    rama para "reenviar por enlace vencido o roto"; respuesta de la vista
    previa fiel al motivo; la prueba de serialización comprueba que el
    segundo hilo estaba efectivamente bloqueado.
    Hecho (ruta: delegada, un escritor; sin cambios de esquema ni de
    permisos). Correo A en párrafos corridos (fijado por prueba); enlace
    consumido responde según el estado actual; "Habilitar" sólo con el
    ciclo en `pending_email_verification` y el cupo realmente agotado (si
    ya está `active`, el aviso se resuelve sin efecto; en otro estado no se
    aplica nada y el administrador recibe "No se habilitó nada."); sin
    "??:??" (incidente + aviso neutral); retirados `TEXTO_ESTADO_CAMBIO` y
    `TEXTO_ENLACE_INVALIDO` (ningún camino alcanzable dice "escribime y lo
    vemos" ni "pedime que te lo reenvíe"); respuestas del bot de
    administración deduplicadas por toque (`callback_query.id`); una sola
    rama para reenviar por enlace vencido o roto; prueba de serialización
    que comprueba el bloqueo. Casos sin texto aprobado resueltos con el
    aviso neutral existente (ciclo `revoked` o inexistente que toca un
    enlace). TDD parcial declarado por el escritor; RED reales en los ítems
    2 y 3. Toque compartido: `gateway._toque_admin` (pasa el id del toque).
    Repetición de la sesión: `287 passed`. Suite completa del escritor:
    `4 failed, 1224 passed` (las 4 de fecha fija de `main`).
    Revisión RDD `review-9ab28ed86c392725` (riesgo medio, consentida):
    aprobada; reconocimiento emitido. Seguimientos que pasan a G1e: enlace
    consumido con ciclo pendiente sin envío vigente debe usar el mismo
    enrutador por estado; el cupo de 5 y el conteo desde el último
    `intento_habilitado` viven en un solo lugar (la base), no duplicados en
    `avisos_admin`; pruebas sin mezclar reloj fijo y reloj real; pruebas del
    respaldo neutral de `_responder_estado_actual` y de `pending_welcome`;
    registrar cuando un toque llega sin id.
  - [x] **G1d-c — Unificación con los avisos al administrador de `main`
    (decisión del usuario, 2026-09-28).** `main` construyó en paralelo
    (T28) el aviso de cada incidente al administrador por el bot de
    administración: `registrar_incidente` como punto único de escritura en
    `incident`, cola `admin_notice` (migración 0017) con reintentos,
    `despachar_avisos_admin`, designación con `python -m prisma
    administrador` y lectura del bot en modo local. Decisión: una sola vía
    hacia el administrador, la de `main`. Los avisos del alta con correo se
    entregan por esa cola (con botones); los incidentes de esta rama pasan
    por `registrar_incidente`; se conservan el estado leído/resuelto de
    `aviso_administrativo` y los botones Marcar leído / Habilitar un nuevo
    intento; se eliminan la cola de entrega y las respuestas propias
    (`aviso_administrativo_entrega`, `aviso_administrativo_respuesta`) y su
    despacho. Integración: respaldo de la rama en
    `auxiliar/alta-y-google-pre-unificacion` (`65facaf`); la rama se rehízo
    sobre `main` (`10950c6`) aplicando todo su diff como un solo parche y
    resolviendo los conflictos una vez (`cli.py`, `local.py`,
    `tests/conftest.py`, `tests/test_avisos_admin.py`).
    Hecho (ruta: delegada, un escritor). `admin_notice` (de `main`) se
    extiende desde la migración 0100 de esta rama: `incident_id` pasa a
    opcional, `aviso_administrativo_id` y `botones`, y la función
    `avisar_aviso_administrativo_admin` (sólo `prisma_admin`). Las
    respuestas puntuales del bot van por una tabla hermana, `admin_reply`,
    con el mismo despacho (una prueba de `main` cuenta todas las filas de
    `admin_notice`, y esas pruebas quedan idénticas a `main`). Un solo
    despacho: `ciclo.despachar_admin` reconcilia los avisos del alta y
    despacha avisos y respuestas. Los incidentes de la rama pasan por
    `incidentes.registrar_incidente`; se corrigió una importación rota tras
    el cambio de `main` (`gateway._registrar_incidente` ya no existe). Se
    eliminaron `aviso_administrativo_entrega`, `aviso_administrativo_respuesta`
    y todo el despacho propio. Pruebas propias en
    `tests/test_avisos_alta_correo.py`; `tests/test_avisos_admin.py` idéntico
    a `main`. Toques a archivos de `main`, mínimos: `despachador.py`
    (botones en la entrega y `despachar_respuestas_admin`), `ciclo.py`
    (reconciliación y respuestas en el mismo ciclo), `incidentes.py`
    (referencia `admin_reply`), `gateway.py` (red de contención del canal
    por `registrar_incidente`). El escritor declaró que no fue TDD estricto
    (implementación y pruebas juntas). Suite del escritor: `1288 passed,
    108 deselected`; repetición de la sesión: `304 passed` en las pruebas
    relacionadas.
    Revisión: el candidato único (10.529 líneas) excedió el presupuesto del
    revisor (`lens_context_budget_exceeded`, sin autoridad creada); se
    partió en 6 commits encadenados (respaldo del commit único en
    `auxiliar/alta-y-google-unificada-un-commit`) y se revisaron los 5 con
    código, todos aprobados con consentimiento del usuario y reconocidos:
    `review-58e2529951ee4e59` (esquema), `review-91d147d2494593a2` (capa
    de datos), `review-e44c3c68c130e7f5` (unificación),
    `review-220c54b04c7c78f3` (recorrido/gateway/cli, cuatro lentes),
    `review-1083f9b7bcb58c4b` (pruebas). Suite sobre la rama rebasada:
    `1306 passed, 108 deselected`.
  - [x] **G1d-c2 — Correcciones de las revisiones de la rama unificada.**
    (1) Filtro de dominios salteable por "Cambiar correo a X": toda
    dirección pasa por la misma validación. (2) Sin emisor configurado,
    cada intento crea un incidente y un aviso nuevos: deduplicar (un aviso
    `correo_sin_emisor` pendiente por espacio). (3) `ciclo.despachar_admin`:
    la reconciliación de avisos del alta queda aislada (savepoint): un
    error suyo nunca frena la entrega de los avisos de incidente de `main`.
    (4) Pruebas del despacho real de `admin_reply` (envío, reintento,
    agotado, incidente). (5) Reactivación con un ciclo ya `active`: la
    persona recibe un mensaje (la bienvenida vigente), nunca silencio. (6)
    `admin_notice`: exactamente una referencia (incidente o aviso), no
    ninguna; comentario del esquema coherente con `admin_reply`. (7) Un
    ciclo trabado a mitad del alta se puede revocar/reiniciar por evento
    (hoy sólo desde `active`). (8) `marcar_leido`/`marcar_resuelto`
    informan si cambiaron algo; `habilitado()`/`dominios_permitidos()`
    toleran un valor inválido (tratar como apagado / sin restricción, con
    incidente). (9) El enlace consumido usa el mismo enrutador por estado
    (una sola copia). (10) La fixture `sin_activar` usa
    `monkeypatch.setenv`. (11) El envío del correo con el enlace ocurre
    dentro de la transacción: documentar el límite honestamente o mover el
    envío después del commit con reconciliación (decidir en la unidad).
    Hecho (ruta: delegada, un escritor). Una sola validación de correo para
    todos los caminos; aviso `correo_sin_emisor` e incidente deduplicados
    por espacio; reconciliación aislada en savepoint en
    `ciclo.despachar_admin`; pruebas del despacho de `admin_reply`;
    reactivación con ciclo en `pending_email_verification` o `active`
    responde por el enrutador de estado (no `onboarding.bienvenida`,
    excluida por C6 con la clave encendida); `admin_notice` exige
    exactamente una referencia; revocar desde cualquier estado previo a
    `active`; `marcar_leido`/`marcar_resuelto` devuelven si cambiaron algo;
    configuración inválida → apagado/sin restricción + incidente; un solo
    enrutador para el enlace consumido; límite de envío dentro de la
    transacción documentado. Sin textos nuevos ni cambios de permisos. TDD
    parcial declarado por el escritor. Toque a `main`: `ciclo.py`
    (savepoint). Suite del escritor: `1323 passed, 108 deselected`.
    Rebase sobre `main` (`4f41c0c`) con un conflicto de una línea de
    `import` en `despachador.py` (`main` agregó `redactar_secreto_telegram`);
    resolución aprobada por el usuario: unir la línea sin tocar `main` y
    aplicar la misma protección a `despachar_respuestas_admin`, que guardaba
    el error con el token del bot (RED observado → GREEN).
    Revisión RDD `review-7cf4977599152a66` (riesgo medio, consentida):
    aprobada; reconocimiento emitido. La sesión corrigió sus advertencias
    con RED observado (7 casos): la clave sólo se enciende con el booleano
    JSON `true` (un `1`, un texto o una lista son corruptos → apagada); los
    dominios sólo se leen de una lista de textos; una configuración corrupta
    deja un solo incidente mientras siga pendiente (un aviso por espacio y
    clave hace de candado, porque `prisma_app` no puede leer `incident`).
  - [x] **G1d — Avisos "🛠️ Administración" por el bot de administración.**
    Camino de salida propio (hoy el bot de administración no envía nada y
    `message_outbox` exige `workspace_id`); botones Reenviar correo /
    Cambiar correo con vista previa y confirmación; aviso informativo de
    quiénes faltan dar su correo; texto libre → respuesta breve sin acción.
  - [x] **G1e — Tanda 1** (escenarios de banco `g-` o `TestClient`) con
    A01-A05, X01, X02 y los casos de `01` §9. La Tanda 2 por Telegram real
    espera a G2 (C4).
- [ ] **G2 — Credencial de Google por espacio.** Tabla dedicada sin
  privilegios de `prisma_app` (patrón `acceso_tablero`), cifrado en reposo,
  flujo OAuth mínimo. Depende de las decisiones abiertas 1, 4 y 6.
- [ ] **G3 — Lectura de Calendar.** Consultar agenda por rango, calendario y
  zona, sin inventar disponibilidad ni ampliar la consulta.
- [ ] **G4 — Crear/modificar evento con vista previa y confirmación.**
  Contrato de vista previa de `03-...` §2; estados `prepared/executing/
  executed/failed/cancelled/expired` con "en ejecución" persistido antes de
  llamar a Google; sin reintento automático ante timeout.
  **Requisito agregado por el usuario (2026-09-27)**, tomado de un sistema
  auditado de ingreso de documentos con efectos externos: (1) un estado
  **indeterminado** para cuando no se sabe si Google aplicó el efecto (timeout,
  respuesta perdida): nunca se da por hecho ni por fallido, nunca se reintenta
  solo, queda un incidente y se reconcilia leyendo Google; (2) **relectura
  después de cada mutación**: el recibo que ve la persona sale de lo que Google
  devuelve al volver a leer el evento, no de lo que se pidió; (3) **clave de
  idempotencia por operación**, estable y derivada del acto (no aleatoria), para
  que un reintento no duplique el evento. Probar los tres con dobles del
  adaptador que simulen timeout, respuesta perdida y éxito sin recibo.
- [ ] **G5 — Reuniones y minutas sobre evidencia/aprobación.** Cadencia
  mensual, agenda e informe previo, minuta enlazada desde el registro
  oficial; una minuta nunca cierra una tarea por sí sola.
- [ ] **G6 — Gmail/Drive/Docs según se decida.** Alcance sujeto a las
  decisiones abiertas 2 y 3. Gmail sólo a destinatarios internos.

Necesitan al usuario: G0 (las dos aprobaciones), G2 (decisiones 1/4/6 y el
proyecto de Google Cloud), G3-G4 (cuenta real con datos ficticios), G6
(decisiones 2/3), y cada rebanada una sesión real por Telegram (Tanda 2 de
`VALIDACION`) antes de darla por cerrada.

## Matriz de aceptación G0 (aprobada por el usuario, 2026-09-27)

Responde a la "Instrucción breve para la IA receptora" de `00-LEER-PRIMERO.md`:
capacidades y estados, contratos, permisos y plan de validación. El pack
define el qué; el repositorio, el cómo. Nada de esto habilita efectos
externos: todo nace apagado por espacio (`correo_verificacion.habilitado`,
`google.habilitado` en `workspace_setting`).

### 1. Capacidades y estados

| Rebanada | Capacidad (etiqueta del pack) | Estados | Cómo en este repositorio |
|---|---|---|---|
| G1 | Alta con correo verificado (V) | `pending_welcome` → `awaiting_email` → `pending_email_verification` → `active`; corregir vuelve a `awaiting_email`; `revoked` sólo por revocación explícita; marca aparte `review_required` (causa y fecha) | Tabla append-only de eventos de alta con `workspace_id` y RLS forzada; proyección por disparador (patrón `task_state_event`/`bloquear_estado_directo`); `prisma_app` sólo inserta eventos. Con la clave encendida, `onboarding.activar` emite `pending_welcome` en la misma transacción; con la clave apagada no emite nada |
| G1 | Token de verificación (I) | emitido → reservado (5 min) → consumido / vencido (24 h) | Tabla sin privilegios de `prisma_app`, acceso sólo por funciones `security definer` de `prisma_owner` (patrón `acceso_tablero`); se guarda SHA-256, comparación con `hmac.compare_digest`; hash y reserva se borran al verificar; enlace `https://t.me/{bot}?start=pv_{token}` resuelto en `gateway._activacion` por el prefijo `pv_` |
| G1 | Reenvío y corrección (I) | máx. 3 envíos por hora y 5 por ciclo (incluye el inicial); reenviar renueva hash, recibo y vencimiento | Límites contados sobre los eventos de envío, no sobre un contador mutable |
| G1 | Contacto verificado (V) | un correo activo por integrante; normalizado (trim + minúsculas) | Alta idempotente por función estrecha: mismo integrante → no-op; activo de otro integrante del espacio → rechazo |
| G1 | Recuperación administrativa (I/D) | `review_required` hasta resolución; leída ≠ resuelta | Superficie según decisión abierta 5 |
| G2 | Credencial de Google por espacio (V para el uso; D para las cinco puertas) | sin autorizar → vigente → requiere reautorización / revocada | Tabla dedicada sin privilegios de `prisma_app`, cifrada en reposo, eventos de autorización/revocación; scopes habilitados como dato en `workspace_setting`, separados de la credencial; las cinco puertas de `02` §2 se comprueban antes de ofrecer una operación |
| G3 | Consultar agenda (V/D) | lectura sin estado | Herramienta `consultar_agenda` con calendario, rango, zona y máximo explícitos; separa confirmado/tentativo/cancelado/sin respuesta; cero resultados → "No encontré eventos en ese calendario entre estas fechas"; caída → "No pude comprobarlo ahora" + incidente |
| G4 | Crear/modificar/retirar evento, responder invitación (V) | `prepared` → `executing` (persistido antes de llamar) → `executed` / `failed` / `incierto` (P: timeout, sin reintento) ; `cancelled`, `expired` | Herramientas discretas sobre `Preparacion`/`pending_action`; la operación externa lleva registro propio por eventos con clave idempotente y recibo normalizado (`tipo` + id externo). Diseño presentado antes de construir |
| G5 | Reunión mensual, agenda e informe previo, minuta (D/P) | reunión: programada → anunciada (−8 días, 15:00) → agenda publicada (−2 días, 16:00) → realizada; reprogramar invalida preparaciones | Cadencia como dato; acuerdos entran por el flujo de borrador → tarea existente; la minuta se enlaza (`evidence.drive_file_id` u homólogo) y nunca cierra una tarea |
| G6 | Gmail, Drive, Docs (V en piloto) | mismos estados que G4 | Según decisiones 2 y 3; Gmail sólo a destinatarios internos verificados; Drive sin compartir público ni a dominio |

Fuera: Sheets, Contacts, Meet, Slides, grabación/transcripción, correo externo,
verificación por respuesta de correo (`01` §7), saludo diario e indicador.

### 2. Contratos

- **Mensajes visibles de G1:** los de `01` §5, textuales (bienvenida,
  pedido de correo, "Gracias. Te envié…", "✅ Gracias, {nombre_preferido}…",
  botones **Reenviar correo** / **Cambiar correo**, `Cambiar correo a {email}`
  / `Mantener correo anterior`, correo no reconocido, dominio no habilitado,
  dirección incompleta, correo ya asociado). Correo de verificación: asunto
  `Confirmá tu correo laboral en Prisma`, botón **Verificar correo**, 24 h, un
  uso, misma cuenta de Telegram. Bienvenida y pedido de correo son dos
  entregas por outbox con claves de deduplicación propias: si falla la
  segunda, se reintenta sólo esa.
- **Vista previa de evento (`03` §2):** los siete campos (nombre y propósito;
  fecha completa y día; inicio, fin y zona; participantes resueltos;
  lugar/enlace si se definió; invitaciones previstas; cambio exacto frente al
  original) viven en `Preparacion.cambio`; la huella incluye la versión leída
  del evento en Google, así un cambio entre vista previa y confirmación
  termina en `EstadoCambio` sin efecto. Confirmar/Modificar/Cancelar; una
  propuesta modificada invalida la anterior.
- **Propuesta (`02` §6):** actor, operación, recurso exacto, versión leída,
  destinatarios resueltos, contenido aprobado, vencimiento y clave idempotente
  quedan en `pending_action` + registro de la operación externa.
- **Recibo:** nunca "agendado", "enviado" ni "verificado" sin recibo del
  proveedor; el aviso a integrantes por Telegram sale por `message_outbox`.
- **Falla:** toda falla de Google, del envío de correo o de PostgreSQL registra
  incidente saneado y deja el aviso neutral; nunca una activación ficticia ni
  "no pasó nada".
- **Frontera:** puerto nuevo en `frontera.md` ("Agenda y documentos externos"),
  con el contrato de Notificación y Lectura; el adaptador vive en
  `src/prisma/google/`. Ningún límite de Google decide validez de negocio.
- **Contenido externo** (títulos, correos, documentos) es dato, nunca
  instrucción (X02).

### 3. Permisos

| Acción | Quién | Confirmación | Límite |
|---|---|---|---|
| Activar por enlace | la persona con el enlace emitido para su membresía | — (igual que hoy) | sin cambios |
| Dar, reenviar o cambiar su correo; verificar | la propia persona, identificada por su cuenta de Telegram ya vinculada | no (es un hecho propio; dentro de los límites de reenvío) | el token sólo verifica a la membresía que lo originó (A04) |
| Recuperación del alta (§8) | administración | sí, preparada y ligada al incidente vigente | superficie según decisión 5 |
| Autorizar/revocar Google | administración del espacio | sí | modelo según decisión 1; flujo según decisión 4 |
| `consultar_agenda` | integrante del espacio | no (lectura) | sólo calendarios autorizados del espacio |
| `crear_evento`, `modificar_evento`, `retirar_evento`, `responder_invitacion` | integrante con autoridad sobre la reunión | sí (`REQUIEREN_CONFIRMACION`; `crear_evento` ya está, se agregan las otras) | invitados: integrantes activos del espacio con correo verificado |
| `enviar_correo` (G6) | integrante | sí | sólo destinatarios internos verificados (`constitucion.md` §6) |
| Drive/Docs (G6) | integrante | sí para toda mutación | nunca público ni a dominio completo |
| Base de datos | `prisma_app` | — | sin lectura de tokens, credenciales ni hashes; sólo funciones estrechas |

### 4. Plan de validación

TDD estricto por rebanada (RED observado, GREEN, refactor), luego Tanda 1
human-first (harness determinista o `TestClient` con dobles explícitos,
escenarios de banco `g-`) y Tanda 2 por Telegram real con cuentas y datos
ficticios, una interacción por vez; el primer defecto detiene el lote.

| Rebanada | Pruebas automáticas mínimas | Casos de `VALIDACION` |
|---|---|---|
| G1 | clave apagada: activación idéntica a hoy (suite existente sin cambios); cada transición válida y cada inválida rechazada por la base; token vencido, consumido, ajeno, ocupado; límites 3/h y 5/ciclo; correo duplicado; dos correos en una frase; bienvenida parcialmente entregada; falla de envío y de PostgreSQL → incidente + aviso; revocación durante la verificación; dos procesos simultáneos; RLS entre espacios; `prisma_app` sin acceso a tokens; paridad de migración/rollback; `test_capacidades` | A01-A05, X01, X02 y los 17 casos de `01` §9 |
| G2 | `prisma_app` no lee la credencial; aislamiento entre espacios; falta la clave de cifrado → no opera y deja incidente (nunca "sin clave seguimos"); permiso insuficiente; API deshabilitada; revocación | — (base de G3-G6) |
| G3 | rango/calendario/zona explícitos; cero eventos sin ampliar la consulta; caída → "No pude comprobarlo ahora"; título con instrucciones tratado como dato | plantilla G01 aplicada a agenda; X02 |
| G4 | dos confirmaciones concurrentes → una llamada; `executing` persistido antes de llamar; timeout → `incierto`, sin reintento; confirmación vencida; botón viejo tras cancelar; cambio del evento entre vista previa y confirmación; organizador vs. invitado | C01-C03, G02-G04 |
| G5 | último viernes y −8/−2 días (incluido cruce de mes y año); reprogramación invalida preparaciones; minuta que dice "cerrar" no cierra | S01, X01, X02 |
| G6 | destinatario externo rechazado; sin compartir público; borrador ≠ envío | G01-G04, X02 |

### 5. Conflictos qué/cómo y resolución propuesta

| # | Conflicto | Propuesta | ¿Consulta? |
|---|---|---|---|
| C1 | `01` §4: estados como campo; `frontera.md` regla 4: eventos | Proyección por eventos, mismos estados y mensajes | No (cómo) |
| C2 | `02` §5 `workspace_mutate` frente a una herramienta por acción | Herramientas discretas en `REGISTRO` | Aprobada por el usuario (2026-09-27) |
| C3 | `01` §3 pasos 1-4 (solicitud pendiente + revisión administrativa) frente al enlace que la administración ya emite para una membresía concreta y entrega en privado | El enlace emitido es la vinculación decidida explícitamente por la administración que exige `01` §2; se conserva como pasos 1-4 y la revisión administrativa queda para la recuperación de §8 | Aprobada por el usuario (2026-09-27) |
| C4 | El correo de verificación necesita un emisor; el pack usó Gmail de la cuenta autorizada, que es G2 | G1 construye el puerto de envío con doble de prueba; el adaptador real Gmail llega en G2 y la Tanda 2 de G1 espera a G2 | Aprobada por el usuario (2026-09-27). El usuario ya tiene la cuenta de correo de Prisma que servirá de remitente |
| C5 | `01` §4: sin verificar no hay herramientas de negocio; ADR 0010 decisión 2: "sin correo verificado, la persona sigue operando por Telegram exactamente como hoy" | Clave apagada: exactamente como hoy. Clave encendida: el pack (V), el control actúa antes del despacho. `PENDIENTE` qué pasa con quien ya estaba activo al encender la clave | Aprobada por el usuario (2026-09-27) |
| C6 | Bienvenida del pack (`01` §5) frente a `onboarding.bienvenida` (incluye tareas abiertas) | Clave encendida: textos del pack literales; clave apagada: la bienvenida actual | Aprobada por el usuario (2026-09-27) |
| C7 | `constitucion.md` §7 pide confirmación para "correos" | El correo de verificación no es la herramienta `enviar_correo`: lo pide la persona, a su propia dirección, dentro del flujo de alta aprobado (último párrafo de §7) | Aprobada por el usuario (2026-09-27) |
| C8 | `02` §7 exige `executing` durable; `pending_action` no lo tiene | Diseño explícito en G4, presentado antes de construir | En G4 |
| C9 | `reunion_periodica` de `corework.yaml` no la consume el importador, y `importador.py` no está entre los archivos compartidos de esta rama | Decidir al abrir G5 (tocar el importador o cargarla por otra vía) | En G5 |

### Decisiones del usuario para G1

- **Decisión abierta 5 resuelta (2026-09-27): avisos administrativos por el
  bot de administración, separado del bot del equipo.** Administrador ≠
  aprobador: el aprobador decide sobre tareas y trabajo; el administrador
  administra el funcionamiento de Prisma (hoy `platform_role`
  `administrador`), puede ser integrante del equipo o no, y su designación se
  configurará desde el panel de plataforma. Reglas:
  - Todo lo administrativo va por el bot de administración, aunque el
    administrador también sea integrante: su chat del equipo queda sólo para
    su trabajo. Se conserva "el canal manda" (`autoridad.py`) sin
    excepciones.
  - Por Telegram el administrador sólo recibe avisos marcados
    "🛠️ Administración" (texto propio de cada caso) y responde con los
    botones de ese aviso, con vista previa, confirmación y el rol revalidado
    al confirmar. El texto libre nunca concede una acción administrativa;
    recibe una respuesta breve que remite a los botones o al panel.
  - Los avisos persisten en la base hasta marcarse leídos (leído ≠
    resuelto), así el panel de plataforma podrá mostrarlos también cuando
    exista.
  - Las acciones y la configuración complejas quedan para el panel.
  - Registro de la decisión del usuario, que primero consideró recibirlos en
    el chat del equipo y eligió el bot separado para evitar confusión.
- **C5 resuelto (2026-09-27): a quien ya estaba activo se le pide el correo
  sin bloquearlo.** Sigue trabajando normal; Prisma le pide el correo una
  vez, con el mismo recorrido de verificación; sin correo no se lo puede
  invitar por Calendar; la administración puede recibir un aviso
  informativo con quiénes faltan. El bloqueo hasta verificar rige sólo para
  las altas nuevas con la clave encendida.

### Textos del alta con correo aprobados por el usuario (2026-09-28)

Regla general aprobada: ningún mensaje termina en "escribime y lo vemos" ni
deja a la persona sin salida; cada problema trae el paso siguiente listo (un
botón, o Prisma hace sola lo obvio y seguro y lo dice). Cuando hablamos del
correo, se muestra la dirección. Los textos del pack (`01` §5) se mantienen
literales; estos son los que no tienen equivalente en el pack.

- A. Cuerpo del correo: "Hola, {nombre}.

Para terminar tu alta en Prisma
  necesito que confirmes que este es tu correo laboral.

Verificar correo:
  {enlace}

Este enlace vence en 24 horas, sirve una sola vez y tiene que
  abrirse con la misma cuenta de Telegram que usás para hablar con Prisma."
- B1. Dos correos: "Encontré más de un correo en ese mensaje. ¿Cuál de estos
  es el que querés usar?" (un botón por dirección).
- B2. Otra cosa sin verificar: "Te mandé el correo de verificación a
  {correo}. ¿No te llegó?" **[Reenviarlo]** **[Usar otro correo]**.
- B3. Otra dirección con verificación pendiente: "¿Uso {nuevo} en lugar de
  {anterior}?" **[Sí, usar {nuevo}]** **[No, dejar {anterior}]**.
- B4. Mantiene la anterior: "Perfecto, seguimos con el correo anterior."
- B5. Enlace vencido: Prisma manda uno nuevo sola, respetando los límites:
  "Ese enlace venció, así que te mandé uno nuevo a {correo}." (sin envíos
  disponibles → B11 o B12).
- B6. Enlace real abierto desde una cuenta de Telegram que no es la de su
  dueño (integrante o no): "Este enlace tiene que abrirse con la cuenta de
  Telegram que usás con Prisma." El enlace no se consume. Un enlace
  inexistente de una cuenta desconocida no recibe respuesta (como hoy). Un
  enlace roto de un integrante con verificación pendiente: Prisma manda uno
  nuevo sola: "Ese enlace no funciona, así que te mandé uno nuevo a
  {correo}."
- B7. Enlace ya usado y correo ya verificado: "Tu correo ya está
  verificado ✅". B7b. Enlace viejo reemplazado por uno más nuevo: "Ese
  enlace ya no sirve porque te mandé uno más nuevo." **[Reenviar el último]**.
- B8. Doble clic: "Ya estoy procesando esa verificación. Esperá un momento y
  revisá si te llegó la confirmación."
- B9. El estado cambió mientras verificaba: sin texto fijo; Prisma sigue
  desde el estado actual (si falta el correo, lo pide; si ya está
  verificado, lo confirma).
- B10. Reenviar sin nada pendiente: "Todavía no tengo tu correo. Pasámelo y
  te envío la verificación."
- B11. Límite por hora: "Se enviaron varios correos de verificación en la
  última hora. Por seguridad, sólo puedo reenviarte otro a partir de las
  {hh:mm}." (hora local del espacio).
- B12. Cinco envíos agotados: "Se agotaron los envíos de verificación. Ya le
  avisé a administración y te escribo apenas lo destrabe." — sólo cuando el
  aviso efectivamente se entrega (G1d-a) y exista la acción de la
  administración para habilitar un nuevo intento (decisión pendiente de
  G1d); hasta entonces se mantiene "Quedó registrado para que
  administración te ayude."
- C. Verificación en modo `existente`: "✅ Gracias, {nombre}. Tu correo quedó
  verificado."
- D. Sin variantes sin nombre: el nombre lo carga la administración al
  definir el equipo (pack o entrevista, `nucleo/alta-de-equipo.md` Bloque 2)
  y es obligatorio. Hallazgo para `main`: la base acepta `nombre = ''`
  (sólo `not null`) y el importador no lo valida
  (`src/prisma/importador.py`, `_importar_personas`); rechazarlo en origen
  es trabajo de la sesión principal.
- E. `{nombre}` = primera palabra del nombre guardado.

- F. Acción de la administración sobre "envíos agotados" (aprobada
  2026-09-28): el aviso por el bot de administración dice "🛠️ Administración
  · {equipo}
{nombre} agotó los 5 envíos del correo de verificación." con
  **[Habilitar un nuevo intento]** **[Marcar leído]**. Habilitar pasa por
  vista previa y confirmación (rol revalidado); abre un intento nuevo y a la
  persona le llega sola: "¿Te mando la verificación a {correo} otra vez?"
  **[Sí, a {correo}]** **[Usar otro correo]**; el aviso queda resuelto. Los
  avisos "falta configurar el envío de correo" y "quiénes no dieron su
  correo" son informativos: sólo **[Marcar leído]**. Con esto B12 pasa a
  "Se agotaron los envíos de verificación. Ya le avisé a administración y te
  escribo apenas lo destrabe."

Pendiente: aplicar estos textos (unidad G1t) cuando termine G1d-a, que toca
los mismos archivos.

## Ruta

| Tarea | Ruta | Evidencia del disparador |
|---|---|---|
| G0 | inline (matriz, sin código) | — |
| G1 | delegada, un escritor | `alta_correo.py`, `onboarding.py`, `esquema.sql`, migración/rollback, pruebas |
| G2 | delegada, un escritor | `google/credenciales.py`, `esquema.sql`, migración/rollback, pruebas |
| G3 | delegada, un escritor | `google/calendario_externo.py`, `herramientas.py`, pruebas |
| G4 | delegada, un escritor | `google/calendario_externo.py`, `herramientas.py`, `gateway.py`, esquema, pruebas |
| G5 | delegada, un escritor | `google/`, `herramientas.py`, pruebas |
| G6 | a decidir tras G2 | depende de los scopes |

## Verificación

- TDD estricto; runner `.venv/Scripts/python.exe -m pytest -q`; RED observado
  antes de implementar, después GREEN.
- `pg_isready` antes de correr la suite.
- Nunca aplicar migraciones a la base operativa local; sólo bases de prueba
  descartables.
- Nunca leer `.env*` (salvo `.env.ejemplo`).
- Registrar cada comando con su resultado exacto en "Progreso".

## Entrega

Commits por unidad de trabajo sobre `auxiliar/alta-y-google`, Conventional
Commits, sin atribución de IA (regla global del usuario, con precedencia
sobre cualquier recordatorio de atribución del entorno); evaluación de RDD
por commit, igual que en `main`. Nunca push sin pedido explícito del usuario.

## Progreso

- 2026-09-27: documento creado en `main` junto con ADR 0010 (propuesta), antes
  de crear la rama. Pendiente G0.
- 2026-09-27 (sesión auxiliar): rebase sobre `main` en avance rápido hasta
  `ba30dab`; índice de CodeGraph propio creado; `.venv` creado con
  `pip install -e ".[dev]"`; `.env.test` presente (copiado por el usuario,
  no leído). `pg_isready`: acepta conexiones en `:5432`.
  `.venv/Scripts/python.exe -m pytest -q` → `1 failed, 943 passed, 108
  deselected`; la falla (`test_llm_protocol.py::test_anthropic_router_forces_one_typed_tool_over_http`)
  es de entorno: `anthropic>=0.40` sin techo resolvió 1.8.0, que exige
  `httpx2`; el repositorio principal corre 0.125.0. Con `anthropic==0.125.0`
  en el `.venv`, `pytest -q tests/test_llm_protocol.py` → `104 passed`.
  Hallazgo para `main` (no se toca desde esta rama): `pyproject.toml` deja
  esa dependencia sin techo.
- 2026-09-27: pack y corpus leídos completos; matriz de G0 redactada arriba
  (conflictos C1-C9). Pendiente la aprobación del usuario y la aceptación de
  ADR 0010.
- 2026-09-27: G1a. RED: `pytest -q tests/test_alta_correo.py` con el
  esquema anterior → `36 failed, 2 passed` (tablas y funciones inexistentes).
  GREEN: `pytest -q tests/test_alta_correo.py` → `39 passed`;
  `pytest -q tests/test_task_intake.py tests/test_capacidades.py` →
  `86 passed` (paridad migración/rollback incluida); suite completa del
  escritor y repetida por la sesión → `992 passed, 108 deselected`.
- 2026-09-28: rebase sobre `main` (12 commits nuevos, incluida la migración
  `0016`) con un conflicto en `src/prisma/cli.py` (el comando `sembrar` de
  `main` y `correo-verificacion` de esta rama en el mismo lugar). Resolución
  aprobada por el usuario: se conservan los dos bloques, el de `main` sin
  cambios (el diff contra `main` en `cli.py` no borra ninguna línea).
  `pytest -q` → `1148 passed, 108 deselected`.
- 2026-09-28: G1d cerrada (G1d-a a G1d-c2). G1e (Tanda 1) hecha:
  `tests/test_alta_correo_tanda1.py` con la matriz de trazabilidad de
  A01-A05, X01, X02 y los 17 casos de `01` §9 (X01 no aplica: es la entrega
  con evidencia de `main`) y 8 escenarios nuevos de punta a punta. Defecto
  real encontrado (caso 16, "reinicio", RED → GREEN): `db.conectar()` y
  `gateway.procesar_update()` dejaban la conexión en una transacción
  abierta, así que el `/start` (verificación y también la activación por
  enlace de `main`) quedaba en un savepoint sin confirmar: la persona veía
  "verificado"/"Listo" y el dato podía perderse si el proceso caía.
  Corregido con un `commit` en cada punto. Hallazgo para `main`: afecta a su
  activación por enlace. Suite del escritor: `1361 passed, 108 deselected`.
  Pendiente de G1: la Tanda 2 por Telegram real, que espera a G2 (Gmail).
- 2026-09-28: revisión RDD `review-030fac3e314b48ba` (configuración
  corrupta + Tanda 1, riesgo medio, consentida): aprobada; reconocimiento
  emitido. Seguimientos menores pendientes: un `null` JSON en la clave o en
  los dominios hoy cuenta como corrupto (debería tratarse como ausente, sin
  incidente); dos lecturas simultáneas de una configuración corrupta pueden
  dejar dos incidentes (el candado del aviso es "consultar y después
  crear").
- Dependencia registrada: el hecho "bienvenida entregada" de G1 queda como
  evento propio para que la unidad de saludo diario de `main` (pack 06)
  pueda contarlo como saludo del día.
- 2026-09-27: **G0 cerrada.** El usuario aprobó la matriz con las
  resoluciones C2-C7 (C4 antes, por separado) y aceptó ADR 0010, cuyo estado
  pasa a `aceptada`. Queda `PENDIENTE` de C5 qué pasa con quien ya estaba
  activo al encender la clave; se pregunta al abrir G1, junto con la decisión
  abierta 5, reducida por C3 a la superficie de la recuperación de §8.

## Cómo arrancar la sesión auxiliar

En el worktree `D:\Proyectos\Prisma-PM-worktrees\alta-y-google`, rama
`auxiliar/alta-y-google`:

1. Leer `AGENTS.md` en su orden de lectura declarado (producto, frontera,
   `nucleo/`, capacidades, STATUS, ROADMAP, INDEX, ADR aplicables).
2. Leer este documento completo.
3. Leer `docs/decisions/0010-correo-verificado-y-google-en-el-producto.md`.
4. Leer el pack completo según "Fuentes funcionales obligatorias", como
   especificación del comportamiento a reproducir, con la regla de
   precedencia de arriba.
5. Preparar el entorno (sección de arriba); pedirle al usuario sólo lo que
   figura en "Cuándo consultar al usuario".
6. Presentar G0. No escribir código hasta cerrarla.
- 2026-09-27 (sesión principal, en `main`): G4 gana un requisito del usuario
  (estado indeterminado, relectura después de cada mutación, clave de
  idempotencia por operación). La rama auxiliar lo recibe con su próximo rebase.
