# ADR 0010: Correo verificado y acceso a Google entran al alcance del producto

- **Estado:** propuesta (pendiente de aceptación del usuario)
- **Fecha:** 2026-09-27
- **Alcance:** `AGENTS.md` (lista de "fuera de alcance"), alta de integrantes
  (`src/leda/onboarding.py`, `db/esquema.sql: activation_token`), un módulo
  nuevo de acceso a Google (`src/leda/google/`, a crear), herramientas nuevas
  en el registro de `src/leda/herramientas.py`, `src/leda/autoridad.py`
  (`REQUIEREN_CONFIRMACION` ya reserva `enviar_correo` y `crear_evento`).
- **Origen:** decisión del usuario, 2026-09-27. Fuente funcional (el *qué* a
  reproducir): `LEDA-PACK-RECONSTRUCCION-20260925/00-LEER-PRIMERO.md`,
  `01-INCORPORACION-E-IDENTIDAD.md`, `02-GOOGLE-ACCESO-Y-OPERACIONES.md`,
  `03-REUNIONES-EVENTOS-Y-AGENDA.md` y
  `VALIDACION-PARA-LA-NUEVA-IMPLEMENTACION.md` describen el comportamiento
  aceptado que este alcance reproduce; el pack documenta la implementación
  anterior del propio usuario. Este documento y el resto del corpus del
  repositorio (`docs/architecture/frontera.md`, `nucleo/`) deciden el *cómo*,
  dentro de la arquitectura multi-tenant vigente.
- **Rama de trabajo:** `auxiliar/alta-y-google`, worktree
  `D:\Proyectos\Leda-PM-worktrees\alta-y-google`, sin efecto sobre `main`
  hasta integración. Ver `odd/tasks/alta-y-google.md`.

## Contexto

`AGENTS.md` lista "agenda o calendarios externos" entre lo que está "fuera del
producto por ahora" y exige "una decisión explícita y documentada" antes de
construirlo. Hoy:

- El alta de integrantes es sólo enlace de activación de Telegram
  (`src/leda/onboarding.py`): ningún correo, ninguna verificación adicional.
- `docs/capacidades.md` ("Diseñado y sin construir") lista sin una sola línea
  de código: Integración de calendario, Correo, Almacenamiento documental,
  Reuniones e informes.
- El esquema ya tiene lugares reservados que nadie llena: `evidence.drive_file_id`
  (`db/esquema.sql`, tabla `evidence`) y `corework.yaml` declara
  `reunion_periodica`, que el importador no consume.
- `src/leda/autoridad.py` ya reserva `enviar_correo` y `crear_evento` en
  `REQUIEREN_CONFIRMACION` — nadie los implementó, pero el núcleo ya los
  anticipó: `nucleo/constitucion.md` §7 lista explícitamente "correos" y
  "creación o modificación de eventos de calendario" entre las acciones que
  exigen vista previa y confirmación humana. Este ADR no cambia `nucleo/`;
  ejercita una capacidad que `nucleo/` ya contemplaba y que `AGENTS.md`
  mantenía fuera del alcance del producto por falta de una decisión
  documentada.

El usuario decidió (2026-09-27) traer dos capacidades al alcance del
producto, tomando como especificación de comportamiento el pack
`LEDA-PACK-RECONSTRUCCION-20260925/` (el detalle completo por sección y por
rebanada vive en "Fuentes funcionales obligatorias" de
`odd/tasks/alta-y-google.md`):

1. **Verificación de correo en el alta**, recuperando el recorrido de
   `01-INCORPORACION-E-IDENTIDAD.md`, **sumada** al enlace de activación
   existente, no en su reemplazo. El correo hace falta para avisar a cada
   persona de reuniones y eventos por Calendar.
2. **Acceso a Google** (Calendar, Gmail, Drive, Docs) para agenda, reuniones y
   documentación, según `02-GOOGLE-ACCESO-Y-OPERACIONES.md` y
   `03-REUNIONES-EVENTOS-Y-AGENDA.md`, construido desde cero: el repositorio
   no tiene ningún código de esto hoy.

## Decisión

1. **Se amplía la lista de `AGENTS.md`.** "Agenda o calendarios externos" deja
   de estar fuera de alcance; queda ordenado por `odd/tasks/alta-y-google.md`
   y sujeto a las restricciones de este documento. El resto de la lista
   ("aprendizaje persistente", "motor genérico de workflows",
   "microservicios", "interfaz administrativa completa") no cambia.
2. **El correo se agrega al alta, no la reemplaza.** `activation_token` y el
   vínculo por Telegram (`onboarding.activar`) siguen siendo el mecanismo que
   asocia una cuenta de Telegram con una persona. El correo es un dato
   adicional de esa misma persona, con su propio ciclo de verificación (token
   propio, de un solo uso, con vencimiento) — nunca sustituye ni adelanta la
   activación por Telegram. Sin correo verificado, la persona sigue operando
   por Telegram exactamente como hoy.
3. **El estado de verificación del correo se escribe por eventos**, igual que
   cualquier otro estado del núcleo (`frontera.md`, regla 4; `mecanica-pm.md`
   §3). El recorrido de estados que describe `01-INCORPORACION-E-IDENTIDAD.md`
   §4 (`pending_welcome → awaiting_email → pending_email_verification →
   active`, con `revoked` y la marca `review_required`) se implementa como
   una proyección sobre una tabla de eventos append-only, con `workspace_id`,
   RLS forzada y política de aislamiento — nunca como una columna que un
   `update` pisa directamente.
4. **Las credenciales de Google son por espacio y nunca se comparten entre
   espacios.** Se crea una tabla nueva (no `workspace_setting`) para la
   credencial de cada espacio, con el mismo patrón de aislamiento de la regla
   1 de `frontera.md` (`workspace_id`, RLS forzada, política
   `aislamiento_espacio`) **y además** sin ningún privilegio directo de
   `leda_app`, siguiendo el precedente ya existente de `acceso_tablero`:
   `revoke all ... from public`, acceso únicamente a través de funciones
   `security definer` propiedad de `leda_owner` (nunca de un superusuario —
   regla 6 y la sección "Cómo se cerró la regla 1" de `frontera.md`) que
   devuelven un token ya vigente, nunca la fila cruda. **Se descarta
   explícitamente `workspace_setting` para este dato**: esa tabla recibe
   `grant select, insert, update, delete ... to leda_app` dentro del bucle
   genérico de RLS de `db/esquema.sql`, así que cualquier proceso del agente
   con `leda_app` podría leer un token guardado ahí en texto plano. El valor
   se cifra en reposo con una clave que vive fuera de la base y fuera de git,
   mismo espíritu que `workspace.bot_token_ref` ("referencia al secreto, nunca
   el token"); el mecanismo exacto de cifrado y custodia de esa clave queda
   `PENDIENTE` (abajo).
5. **Todo efecto de Google pasa por vista previa, confirmación y ejecución
   única**, reusando el mecanismo ya construido
   (`herramientas.Preparacion`/`NecesitaConfirmacion`/`pending_action`, huella
   de estado, ADR 0005) — nunca un camino paralelo. Cada acción nueva
   (`crear_evento`, `consultar_agenda`, `enviar_correo`, etc.) es una
   herramienta más del `REGISTRO` de `src/leda/herramientas.py`, con su
   propia entrada en `autoridad.verificar`; `enviar_correo` y `crear_evento`
   ya están en `REQUIEREN_CONFIRMACION`.
6. **Las notificaciones a personas del equipo siguen saliendo por
   `message_outbox`.** Un correo o un evento de Calendar no es un mensaje de
   outbox — es un efecto externo directo, con su propio recibo
   (`draftId`/`eventId`/`file.id`, según el producto) — pero cuando ese efecto
   genera un aviso a una persona del equipo por Telegram (p. ej. "se creó la
   reunión del jueves"), ese aviso sí es un mensaje de outbox como cualquiera.
7. **El núcleo no conoce a Google.** Se agrega un puerto nuevo a la tabla de
   `frontera.md`, con el mismo contrato que hoy tienen Notificación y
   Lectura: el núcleo expresa "crear un evento con estas personas en este
   horario", nunca una llamada a la API de Calendar. El adaptador concreto
   vive en un módulo nuevo (`src/leda/google/`).
8. **Ningún límite de la API de Google decide la validez de un dato de
   negocio** (regla 3 de `frontera.md`): el máximo de asistentes de un evento
   o el tamaño de un adjunto de Gmail son límites del adaptador de salida,
   nunca una razón para que el núcleo rechace una tarea o una evidencia.
9. **Gmail nunca envía fuera del equipo.** `nucleo/constitucion.md` §6
   prohíbe absolutamente "enviar comunicaciones fuera del equipo en nombre de
   la empresa"; esta decisión no lo cambia ni lo puede cambiar. El scope de
   Gmail queda acotado a destinatarios internos del espacio — coincide con el
   límite que `02-GOOGLE-ACCESO-Y-OPERACIONES.md` ya señala sobre la
   evidencia histórica.
10. **Todo lo nuevo queda apagado por defecto en cada espacio** hasta que se
    active explícitamente: integrar el código no cambia el comportamiento de
    ningún cliente.

## Qué queda fuera de esta decisión

- Sheets, Contacts (más allá de lectura), Meet y Slides:
  `02-GOOGLE-ACCESO-Y-OPERACIONES.md` §4 y §10 marcan evidencia insuficiente
  para tratarlos como capacidad acreditada.
- Grabación, transcripción automática o asistencia automática a Meet, y
  generación automática de actas: `03-REUNIONES-EVENTOS-Y-AGENDA.md` §7 los
  señala como no acreditados.
- Envío de correo a destinatarios externos a la organización: prohibido por
  `nucleo/constitucion.md` §6, sin excepción posible desde un ADR.
- La "alternativa por respuesta de correo" de
  `01-INCORPORACION-E-IDENTIDAD.md` §7 como mecanismo primario de
  verificación: el propio pack la marca D/P con un límite explícito; si se
  construye, es una unidad separada.
- El saludo diario y el indicador de Telegram (packs 05 y 06): son unidades de
  la línea principal, no de esta decisión.
- Aplicación móvil, exportación de configuración y las capacidades de
  producción del "Horizonte posterior" de `docs/ROADMAP.md`.
- Cualquier cambio a `nucleo/` o a la mecánica de cierre de tareas y objetivos
  ya decidida por ADR 0008/0009.

## Restricciones que gobiernan cualquier diseño posterior

- **Aislamiento multi-tenant (regla 1 de `frontera.md`):** toda tabla nueva
  lleva `workspace_id`, RLS forzada y política `aislamiento_espacio`; ninguna
  credencial de Google de un espacio es alcanzable desde otro.
- **Secretos fuera del alcance de `leda_app`:** ninguna credencial (token de
  acceso, refresh token, client secret) se guarda en una fila que `leda_app`
  pueda leer de forma directa. El patrón es `acceso_tablero`.
- **El núcleo no conoce el transporte de Google** (regla 2).
- **Ningún límite de Google decide validez de negocio** (regla 3).
- **Todo se escribe por eventos** (regla 4).
- **La configuración de cada cliente (scopes habilitados, si Gmail está
  activo, cadencia de la reunión mensual) es dato en `workspace_setting`**,
  nunca código (regla 5), separada siempre de la credencial en sí.
- **La autoridad se revalida en la frontera** (regla 6): cada herramienta
  nueva pasa por `autoridad.verificar` y por su propio `preparar`.
- **Efectos no transaccionales:** llamar a Google es un efecto externo que no
  participa de la transacción de PostgreSQL. `02-GOOGLE-ACCESO-Y-OPERACIONES.md`
  §7 exige persistir la transición a "en ejecución" **antes** de llamar y no
  reintentar solo ante un timeout. `pending_action`/`Preparacion` no tienen
  hoy ese concepto; el diseño de G4 lo resuelve explícitamente.
- **Nunca fallar en silencio:** toda falla de un efecto externo registra un
  incidente y deja a la persona un aviso neutral; nunca se informa "no pasó
  nada" sin saberlo.

## Alternativas consideradas

- **Guardar el token de Google en `workspace_setting`.** Rechazada: esa tabla
  ya tiene `select` para `leda_app`; cualquier herramienta del agente podría
  leer el token.
- **Una operación genérica `workspace_mutate` discriminada por
  recurso/acción**, como describe `02-GOOGLE-ACCESO-Y-OPERACIONES.md` §5 sobre
  el sistema histórico. Ajena al patrón de este repositorio (una herramienta
  por acción en `herramientas.REGISTRO`, con su `accion` en `autoridad.py`);
  adoptarla exigiría una capa de autoridad paralela. Se prefieren herramientas
  discretas; queda para confirmar con el usuario en G0, no se decide en
  silencio.
- **Modelar la verificación de correo como una columna mutable.** Rechazada:
  contradice la regla 4 de `frontera.md` y la auditoría de
  `nucleo/constitucion.md` §12.
- **Esperar al panel de plataforma o al tablero de cliente para alojar el
  consentimiento OAuth y la revisión administrativa del alta.** Ninguna de
  las dos superficies existe; esperar bloquearía esta unidad. Queda como
  decisión abierta.

## Consecuencias

- Al aceptarse este ADR, la sesión principal actualiza `AGENTS.md` en `main`
  para reflejar que "agenda o calendarios externos" ya no está fuera de
  alcance. La rama auxiliar no toca `AGENTS.md`.
- Se agregan tablas nuevas al esquema (eventos de verificación de correo,
  credencial de Google por espacio) y un módulo de adaptador
  (`src/leda/google/`); nada llega a `main` hasta que la rama auxiliar se
  integre.
- `docs/capacidades.md` sigue describiendo el estado de `main`; se actualiza
  al integrar.

## Decisiones abiertas (`PENDIENTE`, requieren al usuario)

1. **Modelo de OAuth:** una cuenta por espacio autorizada una vez por su
   administrador (paralelo a `workspace.bot_token_ref`) o OAuth por
   integrante (cada persona autoriza su propia cuenta). La primera es más
   simple de arrancar sin panel de plataforma; la segunda respeta mejor
   "quién hizo qué" en Calendar/Gmail y la distinción organizador/invitado.
2. **Qué scopes se piden en la primera rebanada.** Mínimo razonable: Calendar
   (lectura y escritura acotada). ¿Gmail y Drive/Docs entran en el primer
   corte o quedan para G6?
3. **Si el envío de Gmail está en el alcance inicial.**
4. **Dónde vive el flujo de consentimiento OAuth** (redirect/callback) sin
   panel de plataforma ni tablero de cliente construidos: ¿un endpoint mínimo
   dedicado o esperar a una de esas superficies?
5. **Dónde vive la revisión administrativa del alta con correo**
   (`01-INCORPORACION-E-IDENTIDAD.md` §3, paso 3): ¿el bot de administración
   existente o el panel de plataforma, todavía sin construir?
6. **Cifrado en reposo de las credenciales:** mecanismo, esquema de clave,
   rotación y dónde vive la clave.

Estas seis quedan para el usuario; ninguna rebanada de
`odd/tasks/alta-y-google.md` las decide por su cuenta.
