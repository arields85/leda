# Plataforma, porción 2: la puerta de administración y la carga de tareas

**Rama:** `feat/plataforma` · **Carpeta:** `D:\Proyectos\Leda-PM-worktrees\plataforma`
**Abierta:** 2026-10-12 · **Copia en Engram:** tema `odd/plataforma-p2/tasks` (proyecto `prisma-pm`)
**Diseño:** [ADR 0022](../../docs/decisions/0022-plataforma-web-de-tareas.md), decisiones 6, 7, 9, 10, 11, 12,
15 y 16.2. La porción anterior, en [`plataforma-p1.md`](plataforma-p1.md).

## Objetivo

Que un administrador cargue una tarea comprometida desde la web, por la puerta de administración, con
los controles de la decisión 9, su evento, su auditoría (quién la cargó y quién la decidió) y sin poder
romper el aislamiento entre espacios.

## Por qué ahora, antes de probar la porción 1 en el celular

El ADR pide probar cada porción en el celular antes de la siguiente. El usuario lo salteó esta vez
(2026-10-12: "saltemos la regla en esta ocasión así ganamos tiempo hasta que pueda hacer las pruebas"):
él hace la prueba por Telegram y la de la porción 1 en el celular; mientras tanto se construye esta.

## Alcance

- **La puerta de administración** (decisiones 10 y 12): enlace de un solo uso y sesión de un
  administrador de plataforma, con su propia cookie, separada de la del equipo. Abarca todos los
  espacios; el enlace lo emite por ahora un comando de consola (como en la porción 1). Que lo ofrezca el
  bot de administración toca el Motor: va después de juntar las ramas.
- **La carga en la base** (decisiones 9, 11 y 15): una función `security definer` que valida, escribe la
  tarea y su evento `asignada` y deja la auditoría. El espacio lo elige el administrador entre los que
  existen y la función comprueba en la base que su rol de plataforma está vigente: nunca se confía en el
  valor sin esa comprobación (riesgo 4 de `docs/STATUS.md`). Un doble envío del formulario no carga dos
  tareas (clave de un solo uso).
- **El formulario** (decisión 6 y la vista ancha): en el aspecto "9 · Terminal", pensado para la
  computadora y usable en el celular.

**Fuera de esta porción, por ahora:**
- Los avisos de la decisión 7 (al responsable y a quien revisa): son avisos del motor; después de juntar
  las ramas.
- Que Leda proponga un criterio comprobable cuando el escrito es vago: usa la IA real; necesita permiso
  para probarlo.
- Lo que el usuario todavía no decidió (abajo).

## Restricciones

- No tocar `src/leda/motor/` ni las bases `leda`, `leda_flujo` y `leda_motor`.
- Migraciones desde la `0061` (la `0060` es de la P1-6), cada una con su rollback y su ensayo de paridad;
  `db/esquema.sql` al día; tablas nuevas en el lazo de RLS o declaradas como excepción con su porqué.
- Las mismas de la porción 1 (`plataforma-p1.md`, "Restricciones").

## Tareas

Ruta: un escritor delegado por tarea (dos o más archivos no triviales cada una).

- [x] **P2-1 · La puerta de administración:** tablas del enlace y de la sesión del administrador
      (sin espacio: un administrador abarca todos), canje con el botón "Entrar", cookie propia, corte
      de sesiones, comando `enlace-admin` y `/app/admin/api/yo`. Garantías: un integrante sin rol de
      plataforma no abre la puerta; un rol revocado corta la sesión en el pedido siguiente; la cookie del
      equipo no abre la de administración ni al revés.
- [x] **P2-2 · La carga en la base:** el día hábil del espacio en SQL (`work_calendar` y `holiday`, como
      `calendario.es_habil`); la función de carga con los controles de la decisión 9 (objetivo,
      responsable, fecha, criterio y evidencia; fecha hábil y no pasada; integrante activo; quien la
      hace no la revisa, incluido el caso de la autoridad final sin aprobador); el evento `asignada`; la
      auditoría con quién la cargó y quién la decidió; la clave de un solo uso. La API de escritura con
      protección contra pedidos cruzados.
- [x] **P2-3 · El formulario:** elegir espacio, objetivo, responsable (con "sin conectar" a la vista),
      fecha (sólo días hábiles), criterio y evidencia (la de la política del área como punto de
      partida); vista previa y confirmación; la vista ancha de escritorio.
- [x] **P2-4 · Documentos:** `docs/capacidades.md`, `docs/product/plataforma-pendientes.md`,
      `PRUEBA-LOCAL.md` y este documento con la evidencia.

## Para decidir (el usuario)

Mientras no se decida, lo más restrictivo; abrirlo después no rehace nada.

1. **Los objetivos.** Toda tarea cuelga de un objetivo, pero el ADR no dice quién crea los objetivos ni
   dónde. Hoy los crea sólo el paquete del espacio al importarse (uno por frente). Mientras tanto, el
   formulario deja elegir sólo entre los objetivos que ya existen.
2. **Las esperas.** Si "esta tarea espera a aquella" se carga en el mismo formulario. Mientras tanto, no.
3. **Quién "decidió" la tarea.** La auditoría guarda quién la decidió (ADR 0017, decisión 2). Mientras
   tanto, el formulario pide elegir a un integrante activo del espacio, sin restringir su rol.

## Criterio de aceptación

Las garantías de la carga y de la puerta, en verde; la suite `tests/garantias` completa, en verde; cada
commit de código revisado por RDD; una tarea cargada desde la web aparece en "Tus tareas" de su
responsable.

## Progreso y evidencia

### P2-1 · La puerta de administración (2026-10-12)

**Ruta:** delegated (2+ non-trivial files): migración, esquema, `web_app.py`, `cli.py` y sus pruebas.

**Qué quedó:**
- Migración `0061_la_puerta_de_administracion.sql` (con su rollback y `db/esquema.sql` al día):
  `enlace_de_administracion` y `sesion_de_administracion`, de un `app_user` y sin `workspace_id`
  (un administrador abarca todos los espacios), sin política por espacio y sin ningún privilegio
  para `leda_app`. Funciones `security definer` de `leda_owner`: `emitir_enlace_de_administracion`
  y `cortar_sesiones_de_administrador` sólo para `leda_admin` (la consola);
  `canjear_enlace_de_administracion`, `sesion_de_administracion_vigente` y
  `cerrar_sesion_de_administracion` (la sesión propia, por el hash de su token) sólo para
  `leda_app`. El rol `administrador` de `platform_role` se comprueba al emitir, al canjear y en
  cada pedido; revocado, la sesión queda cortada (`dejo_de_ser_administrador`). Auditoría sin
  espacio, aunque quien llama tenga uno fijado (`auditar_acceso_de_administracion`).
- `web_app.py`: `GET` y `POST /app/admin/entrar/{token}` (el mismo botón y las mismas cabeceras
  que la porción 1), cookie `leda_admin` (`HttpOnly`, `Secure`, `SameSite=Strict`,
  `Path=/app/admin`, 400 días), `GET /app/admin/api/yo` (nombre y espacios) y
  `POST /app/admin/salir`. Las páginas de `/app/admin/` son las de la web; su API, su enlace y
  salir nunca caen en el índice.
- `cli.py`: `python -m leda enlace-admin <nombre>` y `cortar-sesiones-admin <nombre>`; a quien no
  tiene el rol vigente, no.
- Pruebas: `tests/garantias/test_puerta_de_administracion.py` (nueva), más
  `test_web_servida.py`, `test_capacidades.py` (`TABLAS_POR_FUNCION`), `test_migraciones.py`
  (`TABLAS_DE_LA_ADMINISTRACION`) y `tests/test_cli_plataforma.py`.

**Evidencia:**
- RED, antes del código: `pytest -q tests/garantias/test_puerta_de_administracion.py
  tests/garantias/test_web_servida.py tests/test_cli_plataforma.py` → 34 failed, 27 passed.
- GREEN, lo mismo → 61 passed.
- `pytest -q tests/garantias/test_puerta_de_administracion.py tests/garantias/test_enlace_y_sesion.py
  tests/garantias/test_api_de_la_plataforma.py tests/garantias/test_web_servida.py
  tests/garantias/test_capacidades.py tests/garantias/test_frontera.py
  tests/garantias/test_aislamiento.py tests/garantias/test_migraciones.py
  tests/test_cli_plataforma.py` (con `LEDA_TEST_DB_URL` al servidor local de pruebas) →
  155 passed (16 min 30 s), con el ensayo de paridad y de rollback de la `0061`.
- Commit de código y pruebas: `16f630ca`. La suite `tests/garantias` completa y la revisión RDD:
  `PENDIENTE` (las corre el coordinador).

**Para confirmar con el usuario** (anotado en `docs/product/plataforma-pendientes.md`): el enlace
de la administración no vence por tiempo, como el del equipo; el rol `operador` no abre la
puerta; `/app/admin/api/yo` lista todos los espacios, también los importados sin activar.

### P2-2 · La carga en la base (2026-10-12)

**Ruta:** delegated (2+ non-trivial files): migración, esquema, `web_app.py` y sus pruebas.

**Qué quedó:**
- Migración `0062_la_carga_de_tareas_desde_la_web.sql` (con su rollback y `db/esquema.sql` al
  día). `es_dia_habil(espacio, fecha)`: el día hábil en SQL, igual que `Calendario.es_habil`
  (sin calendario, ninguno). `opciones_de_la_carga` y `cargar_tarea`, `security definer` de
  `leda_owner` y sólo para `leda_app`: comprueban la sesión de administración en cada llamada y
  que el espacio exista, y fijan ellas mismas ese espacio (la RLS no deja encontrar un id de
  otro). La carga devuelve los rechazos de la decisión 9 todos juntos como datos (`campo`,
  `motivo`) y los avisos que no bloquean; escribe la tarea (área del responsable, fecha al
  cierre de la jornada del espacio), su evento `asignada` (actor `persona`: el administrador) y
  la auditoría `cargar_tarea` en el espacio de la tarea, con quién la cargó, quién la decidió
  (`decision_declarada_al_cargar`), quién la revisa y las versiones. `carga_de_tarea`: la clave
  de un solo uso, con espacio, RLS forzada y sin privilegios para `leda_app`.
- `web_app.py`: `GET /app/admin/api/espacios/{id}/opciones` y `POST
  /app/admin/api/espacios/{id}/tareas` (JSON; 201, 200 si la clave ya cargó, 422 con los
  rechazos en palabras, 401, 404; 403 desde otro sitio y 415 si no es JSON).
- Pruebas: `tests/garantias/test_carga_de_tareas.py` (nueva), más `test_capacidades.py`
  (`TABLAS_POR_FUNCION`) y `test_migraciones.py` (`TABLAS_DEL_MOTOR`).
- La versión de cada fila (decisión 15) es para editar (porción 3): crear no pisa nada, así
  que no se agregó.

**Decisiones del escritor, para confirmar** (anotadas en `docs/product/plataforma-pendientes.md`):
- Quién revisa es la regla única de la base (`quien_revisa_la_tarea`, sin caer a la autoridad
  final, porque el motor no lo hace): sin un aprobador activo no se carga
  (`sin_quien_la_revise`); la autoridad final sin aprobador, `la_hace_y_la_revisa`.
- Sólo tipos de evidencia que la política del área conoce: uno desconocido no lo cubriría
  ninguna pieza y la tarea no se cerraría nunca.
- La fecha vence al cierre de la jornada del espacio; los topes de texto son los del borrador,
  en caracteres.

**Evidencia:**
- RED, antes del código: `pytest -q tests/garantias/test_carga_de_tareas.py` → 32 failed.
- GREEN, lo mismo → 32 passed (54 s).
- `pytest -q tests/garantias/test_carga_de_tareas.py tests/garantias/test_puerta_de_administracion.py
  tests/garantias/test_quien_ve_que.py tests/garantias/test_capacidades.py
  tests/garantias/test_frontera.py tests/garantias/test_aislamiento.py
  tests/garantias/test_migraciones.py` (con `LEDA_TEST_DB_URL` al servidor local de pruebas) →
  116 passed (15 min 11 s), con el ensayo de paridad y de rollback de la `0062`.
- Commit de código y pruebas: `f6a40067`. La suite `tests/garantias` completa y la revisión RDD:
  `PENDIENTE` (las corre el coordinador).

### Arreglo de la revisión de la P2-1: la sesión es del rol vigente (2026-10-12)

**Ruta:** delegated (2+ non-trivial files): migración, rollback, esquema y sus pruebas.

La revisión RDD `review-2bb3704b62fcce34` de la `0061` advirtió: si a un administrador le revocan el
rol y se lo vuelven a otorgar antes del pedido siguiente de su sesión, la sesión vieja seguía
entrando (`sesion_de_administracion_vigente` sólo miraba que el rol estuviera vigente ahora).

**Qué quedó:** migración `0063_la_sesion_es_del_rol_vigente.sql` (con su rollback y
`db/esquema.sql` al día): una sesión creada antes del `otorgado_en` del rol vigente queda cortada
con el mismo motivo y la misma auditoría que la de un rol revocado (`dejo_de_ser_administrador`:
entre su apertura y hoy la persona dejó de serlo, así que no hizo falta un motivo nuevo ni tocar la
restricción); un enlace emitido antes del otorgamiento vigente no se canjea y queda anulado.

**Evidencia:**
- RED, antes del código: `pytest -q tests/garantias/test_puerta_de_administracion.py -k
  "anterior_al_rol or volver_a_otorgar"` → 3 failed.
- GREEN: `pytest -q tests/garantias/test_puerta_de_administracion.py` → 32 passed (46 s);
  `pytest -q tests/garantias/test_migraciones.py` → 16 passed (3 min 48 s), con el ensayo de
  paridad y de rollback de la `0063`.
- Commit: `072972aa`. La revisión RDD: `PENDIENTE` (la corre el coordinador).

### P2-3 · El formulario (2026-10-12)

**Ruta:** delegated (2+ non-trivial files): la web (`web/src/admin/`, `door.ts`, `main.tsx`,
`SignOut.tsx`) y sus pruebas.

**Qué quedó:**
- La misma web elige la puerta por el camino (`/app/admin/`), sin dependencias nuevas (ni React
  Router): `web/src/door.ts`. El servidor ya servía esas páginas (`test_web_servida.py`, sin
  cambios).
- `AdminApp`: el cabezal ("LEDA · ADMINISTRACIÓN · COREWORK", "Cargar tarea", el nombre del
  administrador), "salir" (el mismo componente del equipo, con la acción de esta puerta), un
  selector de espacio si hay más de uno y los estados de sesión cerrada ("entrá con un enlace
  nuevo") y de falla.
- `LoadForm`: los campos alimentados por `/opciones`, con contadores de los topes del servidor;
  quién la hace con su área, "la revisa: …" (o "nadie") y "[SIN CONECTAR]"; la evidencia de la
  política del área, marcada la que pide; "revisar" → la vista previa (`TaskPreview`, con la
  tarjeta del equipo y quién la carga, la decidió y la revisa) → "confirmar" o "volver". Una clave
  por intento (`newKey`: `crypto.randomUUID`, o 32 dígitos hexadecimales sin HTTPS), la misma en
  cada reintento, nueva al cambiar un dato o después de cargar. 201/200: "Tarea cargada." con los
  avisos y "cargar otra"; 422: cada rechazo en su campo (con `aria-invalid`) y los demás en un
  resumen; 401: sesión cerrada; sin red: los datos quedan y "probar de nuevo".
- `DatePicker`: un mes por vez, lunes primero, sólo los días hábiles que ofrecen las opciones son
  botones (los demás, en gris y fuera del orden de tabulación); flechas entre días hábiles (arriba y
  abajo, una semana), Enter o espacio para elegir.
- La vista ancha: desde 1024 px, el formulario a la izquierda y la vista previa a la derecha
  (pegada arriba), hasta 72rem; la puerta del equipo sigue en su columna de 32rem.

**Evidencia:**
- Las pruebas se escribieron junto con el código (no hubo un RED observado antes): 15 en
  `web/src/admin/AdminApp.test.tsx` (formulario con las opciones de mentira, sólo días hábiles,
  flechas, evidencia marcada, contadores, vista previa y "volver", cuerpo y clave al confirmar,
  aviso de fecha posterior, reintento con la misma clave, clave nueva al editar, errores en sus
  campos, 401 al confirmar y al entrar, varios espacios, la clave sin HTTPS) y 1 en
  `web/src/door.test.ts`.
- En `web/`: `npx tsc --noEmit` sin errores; `npx vitest run` → 54 passed (11 archivos);
  `npx vite build` bien.
- Ancho: la web compilada, servida con datos de mentira por un servidor de Node de prueba en el
  puerto 5179 (fuera del repositorio, cortado después), con Chrome sin ventana: dentro de un marco
  de 390 px, `scrollWidth` 390 = ancho 390 en el formulario vacío, lleno y en "revisar"; a 1280 px
  (ventana), `scrollWidth` 1254 = ancho 1254 (sin desborde). Capturas miradas: a 390, una columna;
  a 1280, dos columnas.
- Commit: `37ac3bcc`. La revisión RDD: `PENDIENTE` (la corre el coordinador).

**Decisiones del escritor, para confirmar** (anotadas en `docs/product/plataforma-pendientes.md`):
el espacio elegido no se recuerda entre visitas; cambiar de persona vuelve a marcar la evidencia de
su área; el cliente no valida antes de "revisar" (lo decide la base y vuelve en cada campo).

### Arreglo de la revisión de la P2-2: hoy, no después del cierre (2026-10-12)

**Ruta:** delegated (2+ non-trivial files): migración, rollback, esquema, `web_app.py` y sus
pruebas.

La revisión RDD `review-40c4b218bf40f1fa` de la `0062` advirtió dos cosas: (1) hoy se aceptaba
como fecha aunque ya hubiera cerrado la jornada del espacio, y la tarea nacía vencida; (2)
`json.loads` de un cuerpo muy anidado tira `RecursionError`, no `ValueError`, y daba 500.

**Qué quedó:** migración `0064_hoy_no_despues_del_cierre.sql` (con su rollback y `db/esquema.sql`
al día): `cargar_tarea` rechaza hoy a la hora del cierre (`hora_fin`, en la zona del espacio) o
después (`fecha`, `ya_cerro_el_dia`, "La jornada de hoy ya terminó en este espacio: elegí otro
día."), y `opciones_de_la_carga` ofrece los días hábiles desde mañana en ese caso, así el
calendario del formulario coincide sin cambiar la web. `web_app.py` trata el `RecursionError` como
un cuerpo mal formado (422).

**Evidencia:**
- RED, antes del código: `pytest -q tests/garantias/test_carga_de_tareas.py -k "cerro_la_jornada
  or anidado"` → 3 failed (hoy aceptado a las 18:00, hoy ofrecido, y el cuerpo anidado).
- GREEN: `pytest -q tests/garantias/test_carga_de_tareas.py` → 35 passed (39 s).
- La verificación entera, abajo. Commit: `8e18463d`. La revisión RDD: `PENDIENTE`.

### Verificación de las tres unidades (2026-10-12)

`pytest -q tests/garantias/test_puerta_de_administracion.py tests/garantias/test_migraciones.py
tests/garantias/test_web_servida.py tests/garantias/test_carga_de_tareas.py` (con
`LEDA_TEST_DB_URL` al servidor local de pruebas) → 105 passed (5 min 2 s), sobre los tres commits (`072972aa`, `37ac3bcc`, `8e18463d`), con el ensayo de paridad y de rollback de la `0063` y la `0064`. La suite `tests/garantias` completa: `PENDIENTE` (la corre el coordinador).

### Arreglo de la revisión de la P2-3 (2026-10-12)

**Ruta:** delegated (2+ non-trivial files): `AdminApp.tsx`, `LoadForm.tsx` y sus pruebas.

La revisión RDD `review-7b6e2e7b8d956d75` de `37ac3bcc` advirtió: (1) un 404 de `/opciones`
volvía a pedir `/yo` y, si el espacio seguía en la lista, otra vez las opciones, sin fin; (2)
cambiar un dato renovaba la clave aunque el envío anterior no hubiera tenido respuesta, y si ese
envío sí había cargado la tarea, el reenvío cargaba otra. Ahora: ante el 404 se relee la lista de
espacios una sola vez y se dice "Ese espacio ya no está disponible." (con "probar de nuevo" si
sigue en la lista, o "Elegí otro espacio arriba." si ya no está); y mientras el resultado del
último envío es desconocido (sin red, un 5xx) la clave sigue aunque cambien los datos. Un 422 o
una carga lo resuelven; si el servidor contesta que la clave ya se usó con otros datos (422,
`clave`, `usada_con_otros_datos`), el formulario dice "Puede que ya se haya cargado: fijate en "El
equipo" antes de cargarla de nuevo." con "no está cargada: empezar de nuevo" (clave nueva).
Evidencia: las tres pruebas nuevas que lo cubren fallan con el código anterior (3 failed, 15
passed) y pasan con el nuevo; en `web/`, `npx tsc --noEmit` sin errores, `npx vitest run` → 57
passed, `npx vite build` bien.

### Cierre del coordinador (2026-10-12)

- **Suite entera de garantías**, cada vez en una carpeta aparte (`pytest -q tests/garantias
  tests/test_cli_plataforma.py`): sobre `0c70ea11` (P2-1) 669 passed (22 min); sobre `00432275` (P2-2)
  701 passed (25 min); sobre `f428389e` (P2-3 y los arreglos A y C) 707 passed (20 min).
- **RDD por tramos, todas aprobadas:** `16f630ca` (`review-2bb3704b62fcce34`), `f6a40067`
  (`review-40c4b218bf40f1fa`), `072972aa` (`review-c30e9e7ac000fa0e`), `37ac3bcc`
  (`review-7b6e2e7b8d956d75`), `8e18463d` (`review-c88ebea1b3807c0f`) y `f30665e0`
  (`review-5af4428ea31f40d2`). Las advertencias de peso se arreglaron con su commit (la sesión vieja de
  administración, `072972aa`; hoy después del cierre y el cuerpo anidado, `8e18463d`; el ciclo ante un
  404 y la clave tras un resultado incierto, `f30665e0`).
- **Advertencias sin arreglar:** una sesión creada en el mismo instante que el otorgamiento
  (`0063`, 107-109); el enlace anulado sin auditoría propia (`0063`, 68-71); si desaparece el único
  espacio, la pantalla queda sin salida (`AdminApp.tsx`, 138-143); la rama del campo mal formado sin
  prueba (`LoadForm.tsx`, 151-153); sugerencias de pruebas.
- **Repaso del coordinador:** `npx vitest run` en `web/`: 57 passed.
- `PENDIENTE`: la prueba del usuario en el celular y en la computadora; los avisos de la decisión 7 y
  que el bot de administración ofrezca el enlace (después de juntar las ramas); que Leda proponga un
  criterio comprobable (IA real, con permiso); las tres preguntas de "Para decidir" y si el enlace de
  entrada vence (recomendación: 24 horas).
