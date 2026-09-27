# Alta con correo verificado y acceso a Google (rama auxiliar)

**Estado:** G0 presentada (matriz abajo) — pendiente de aprobación del usuario y aceptación de ADR 0010
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

- [ ] **G0 — Matriz de aceptación y OK del usuario.** Antes de escribir
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

## Matriz de aceptación G0 (propuesta, pendiente de aprobación del usuario)

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
| C2 | `02` §5 `workspace_mutate` frente a una herramienta por acción | Herramientas discretas en `REGISTRO` | Sí, en G0 |
| C3 | `01` §3 pasos 1-4 (solicitud pendiente + revisión administrativa) frente al enlace que la administración ya emite para una membresía concreta y entrega en privado | El enlace emitido es la vinculación decidida explícitamente por la administración que exige `01` §2; se conserva como pasos 1-4 y la revisión administrativa queda para la recuperación de §8 | Sí, en G0 |
| C4 | El correo de verificación necesita un emisor; el pack usó Gmail de la cuenta autorizada, que es G2 | G1 construye el puerto de envío con doble de prueba; el adaptador real Gmail llega en G2 y la Tanda 2 de G1 espera a G2 | Sí, en G0 |
| C5 | `01` §4: sin verificar no hay herramientas de negocio; ADR 0010 decisión 2: "sin correo verificado, la persona sigue operando por Telegram exactamente como hoy" | Clave apagada: exactamente como hoy. Clave encendida: el pack (V), el control actúa antes del despacho. `PENDIENTE` qué pasa con quien ya estaba activo al encender la clave | Sí, en G0 |
| C6 | Bienvenida del pack (`01` §5) frente a `onboarding.bienvenida` (incluye tareas abiertas) | Clave encendida: textos del pack literales; clave apagada: la bienvenida actual | Sí, en G0 |
| C7 | `constitucion.md` §7 pide confirmación para "correos" | El correo de verificación no es la herramienta `enviar_correo`: lo pide la persona, a su propia dirección, dentro del flujo de alta aprobado (último párrafo de §7) | Sí, en G0 |
| C8 | `02` §7 exige `executing` durable; `pending_action` no lo tiene | Diseño explícito en G4, presentado antes de construir | En G4 |
| C9 | `reunion_periodica` de `corework.yaml` no la consume el importador, y `importador.py` no está entre los archivos compartidos de esta rama | Decidir al abrir G5 (tocar el importador o cargarla por otra vía) | En G5 |

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
- Dependencia registrada: el hecho "bienvenida entregada" de G1 queda como
  evento propio para que la unidad de saludo diario de `main` (pack 06)
  pueda contarlo como saludo del día.

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
