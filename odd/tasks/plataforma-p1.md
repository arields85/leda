# La plataforma, porción 1: la puerta del equipo, de sólo lectura

**Rama:** `feat/plataforma` · **Carpeta:** `D:\Proyectos\Leda-PM-worktrees\plataforma` (nacida de la rama
del Motor) · **Abierta:** 2026-10-12 · **Copia en Engram:** tema `odd/plataforma-p1/tasks` (proyecto
`prisma-pm`) · **Diseño:** [ADR 0022](../../docs/decisions/0022-plataforma-web-de-tareas.md), aceptado.

## Objetivo

Que cada integrante vea desde el celular lo mismo que le contaría Leda, según su puesto ("Tus tareas",
"Tu sector", "El equipo"), entrando con un enlace de un solo uso que deja la sesión abierta sin vencimiento
(ADR 0022, decisiones 3, 4, 5, 12, 13, 16.1, 17 y 18).

## Por qué en una rama aparte

La prueba por Telegram de la Fase C es el 2026-10-12 (día) y tiene que probar la Fase C tal como está. La
plataforma se construye en `feat/plataforma`; después de la prueba, la rama del Motor pasa a `main` y la
plataforma suma los arreglos que haya dejado la prueba (usuario, 2026-10-12).

## Alcance de esta noche (sin tocar la conversación)

Entra: la base (enlace de un solo uso y sesión; quién ve qué en listas), la API interna, la web con el
aspecto de la "9 · Terminal" y un comando de consola para emitir y cortar un enlace (para probar sin el chat).

**No entra esta noche** (va después de la prueba por Telegram, con el usuario):
- que Leda ofrezca el acceso por chat y el corte por "perdí el celular" (tocan el motor de conversación:
  primero su conversación de prueba, después una ronda con la IA real con permiso del usuario);
- la prueba en el celular (necesita que la PC sea alcanzable: IP de la red local o un túnel; una cookie
  `Secure` pide HTTPS fuera de `localhost`);
- ninguna ronda con la IA real, nada a `main`, nada remoto.

## Restricciones

- **No tocar `src/leda/motor/`** esta noche: si la prueba de mañana deja arreglos, se suman sin choque.
- **Migraciones desde la `0057`**, cada una con su rollback en `db/rollbacks/` y plegada en
  `db/esquema.sql`; las pruebas las descubren solas y exigen paridad. Si un arreglo de la Fase C necesita
  una migración, la de la plataforma se renumera al juntar las ramas.
- **Garantías de la base** (`tests/garantias/test_aislamiento.py`): toda tabla con `workspace_id` con
  `row level security` forzado o en `EXCEPCIONES_SIN_RLS` sin privilegios para `leda_app`/`leda_gateway`;
  toda función `security definer` con dueño que no saltea RLS, `search_path` fijo terminado en `pg_temp`
  y sin `execute` para PUBLIC. El espacio sale de la sesión, nunca del pedido (decisión 11).
- **Tokens:** sólo el hash SHA-256, como `acceso_tarea` (0036). El enlace sirve una vez; la sesión no
  vence y se revalida en cada pedido (membresía activa); se corta si la persona deja el equipo o si un
  administrador la corta (decisiones 4 y 12).
- **Quién ve qué** (decisión 3): integrante, sus tareas, las que espera de otros y las que otros esperan de
  él, sin los atrasos ajenos; referente (`area.referente_membership_id`), todo su sector con fechas,
  atrasos y bloqueos; autoridad final (`rol.autoridad_final`), todo el espacio, sin rankings. Una sola
  regla en SQL que extiende `puede_ver_tarea` (decisión 13).
- **La web:** React, TypeScript, Vite, Tailwind, Lucide (decisión 17), en `web/`, compilada y servida por
  la misma aplicación (`src/leda/entrada.py`), mismo origen, cookie `HttpOnly`, `Secure`,
  `SameSite=Strict`. Versiones exactas en `package.json`.
- **El aspecto** (decisión 18): oscuro, grises, JetBrains Mono; color sólo en los estados que tienen algo
  (vencida `#FFC14D`, trabada `#FF7A6B`, en curso `#9BE39B`, entregada `#8FD0FF`; en 0, gris); cabezal de
  la "11 · Plano"; barra "C" por días hábiles con "hoy" bajo el segmento blanco y la fecha de entrega bajo
  el último; "quedan N días" arriba de la tarjeta en curso; botón "> contarle algo a leda" (desde la P1-6, "> consultar a leda") blanco, con el
  marco de las tarjetas y sin cursor. Referencia: el lienzo https://claude.ai/artifact/VwC3sCvufFZ7DUkv3yJt7f
  (tableros "9 · Terminal", "9b" y "Barras de progreso"; se leen con la herramienta Artifact, `read`).
- Textos de la interfaz en castellano (como Leda); identificadores como el resto del código.

## Cómo se trabaja en la carpeta de la plataforma

- **Pruebas:** desde `D:\Proyectos\Leda-PM-worktrees\plataforma`, con el Python del Motor y el servidor
  local como base descartable (el superusuario local entra sin contraseña; no hace falta `.env.test`, que
  una regla impide copiar):
  `LEDA_TEST_DB_URL="postgresql://postgres@localhost:5432/postgres" ../motor-de-conversacion/.venv/Scripts/python.exe -m pytest -q <pruebas>`
  (comprobado el 2026-10-12: `tests/garantias/test_pagina_de_la_tarea.py`, 30 passed).
- **Qué código corre** (comprobado el 2026-10-12): el `.venv` del Motor tiene `leda` instalado apuntando a
  `motor-de-conversacion/src`. `pytest` antepone el `src/` de esta carpeta y prueba el código de la
  plataforma; un comando suelto (`python -m leda …`, `python -c …`) corre el del Motor salvo con
  `PYTHONPATH=src`.
- **Nada toca las bases de verdad:** cada corrida crea `leda_test_<azar>` y la borra. Los roles `leda_*`
  son del servidor entero (compartidos con `leda_motor`): ninguna migración crea, altera ni borra roles.
- **El puerto 8000 es de la prueba por Telegram:** ningún servidor (uvicorn, vite) queda corriendo; para
  mirar algo, otro puerto, y se cierra.
- **Node 24 y npm 11** instalados; no hay `package.json` todavía.
- **Commits** en `feat/plataforma`, uno por tarea, sin líneas de atribución. **RDD** por commit de código:
  `tools/rdd_ciclo.py <carpeta temporal> <base>` en una carpeta `../_rdd-<nombre>` desprendida, que se
  borra al terminar. La primera base es `093eb33c` (donde nace la rama).
- La rama se puede subir a `origin` como respaldo (misma autorización que la del Motor).

## Tareas

Ruta: escritor delegado en cada una (dos o más archivos no triviales); el coordinador revisa, corre una
comprobación y hace la revisión RDD. Estimación total: más de 400 líneas; cada tarea es su commit.

- [x] **P1-0 · El guion de la prueba de mañana** (rama del Motor, sólo documentos): comprobar que
      `docs/product/guion-telegram-fase-c-parte-1.md` cubre lo construido después del 2026-10-08 (trabas
      y quién destraba, delegar, apodos, el formato de la cocina, la lista del detalle); si no, sumar los
      pasos que falten, como hilo numerado (quién, texto exacto, lo esperado).
- [x] **P1-1 · El enlace y la sesión** (migración `0057`): tablas del enlace de un solo uso y de la sesión
      (sólo hashes; membresía; creada, último uso, cortada y motivo), funciones `security definer` para
      emitir el enlace, canjearlo por una sesión (una sola vez), leer la sesión vigente (revalida la
      membresía y anota el último uso) y cortarla; auditoría de emitir, canjear y cortar. Pruebas de
      garantías: el enlace no sirve dos veces, una sesión cortada o de alguien que dejó el equipo no
      entra, aislamiento entre espacios, catálogo de dueños y RLS, rollback y paridad.
- [x] **P1-2 · Quién ve qué en listas** (migración `0058`): la función de lista por vista ("tus":
      mías, espero, me esperan; "sector"; "equipo") que extiende `puede_ver_tarea`, sin atrasos ajenos
      para el integrante; qué vistas tiene cada persona. Pruebas por puesto.
- [x] **P1-3 · La API interna:** canje del enlace (`/app/entrar/{token}` → cookie y redirección a la
      web), `/app/api/yo` (quién es y qué vistas tiene) y `/app/api/tareas?vista=…` (panel por estado,
      semana del calendario del espacio con los días en que vence algo, y cada tarea con su estado, su
      fecha, sus días hábiles para la barra y la cadena de esperas); cabeceras como las de la página de
      la tarea; `TestClient` con `https`. Comando de consola para emitir el enlace de una persona y para
      cortar sus sesiones.
- [x] **P1-4 · La web:** `web/` con Vite, React, TypeScript, Tailwind y Lucide; los tokens del aspecto;
      las piezas (cabezal, panel de estados, tira de la semana, tarjeta, barra de días, árbol de esperas,
      botón); "Tus tareas", "Tu sector" y "El equipo"; compilada a `web/dist` y servida en `/app`.
      Comprobaciones: tipos, pruebas de las piezas (vitest), compilación, y una prueba de Python que la
      sirve; control del ancho de un teléfono (390 px).
- [x] **P1-5 · Documentos:** `docs/capacidades.md`, `docs/product/plataforma-pendientes.md`, cómo
      levantarla para probar (`PRUEBA-LOCAL.md`) y este documento con la evidencia.

- [x] **P1-6 · Las decisiones del usuario** (2026-10-12, "Decidido por el usuario", abajo): la fecha,
      el estado, la trabada y la vencida ya hablada de lo que espero (1, 5, 7); las terminadas de 30 días
      (3); la cadena entera (6); el botón "> consultar a leda" con la dirección del bot (8). Lo que cambia
      quién ve qué va en una migración nueva con sus pruebas de garantías.

**Después de la prueba por Telegram** (con el usuario): juntar las ramas; Leda ofrece el acceso por chat
y el corte por "perdí el celular" (conversación de prueba, ronda con la IA real con permiso); la prueba en
el celular del usuario (cierre de la porción).

## Criterio de aceptación

Con datos ficticios, una persona entra con su enlace, la sesión queda abierta, ve exactamente lo que su
puesto le permite con el aspecto de la "9 · Terminal", y el enlace usado o una sesión cortada no entran.
Lo prueba primero `TestClient` y después el usuario en su celular.

## Progreso y evidencia

- 2026-10-12: rama y carpeta creadas desde `093eb33c`; las pruebas corren desde la carpeta (30 passed).
  `leda_motor` al día hasta la `0056` para la prueba de mañana (en la rama del Motor, `6fc7449f`).
- 2026-10-12, noche. **P1-0** (rama del Motor, `6faafce6`): el guion suma la segunda parte, pasos 22 a
  48 (apodos, quién destraba, la pregunta sin contestar, pasar una tarea, enlace y detalle ajeno, la
  lista, el informe al grupo); lo no comprobable, marcado "(a observar)". La prueba del 2026-10-08 había
  dejado "Programar PLC" entregada y "Dashboard" terminada: `leda_motor` se recreó con respaldo
  (`18828013`, detalle en `docs/STATUS.md`).
- **P1-1** (`db782e71`, escritor delegado: dos archivos no triviales): migración `0057`,
  `enlace_de_entrada` y `sesion_web` (sólo hashes, RLS forzado, sin privilegios para `leda_app`), cinco
  funciones `security definer` (emitir, canjear, sesión vigente, cortar una, cortar las de una persona),
  auditoría sin el token. El enlace no vence por tiempo (como la `0036`): deja de servir al canjearse, al
  emitirse otro o al cortarse las sesiones. RED: 25 fallas (`UndefinedFunction`); GREEN: 26 passed.
  `pytest tests/garantias/test_capacidades.py tests/garantias/test_frontera.py`: 7 passed (la de la
  frontera corre todas las garantías en otro proceso). RDD `review-ce739a56c466ff4c`, aprobada.
  Advertencias sin arreglar: dos emisiones simultáneas para la misma persona hacen fallar la segunda con
  un error en vez de reemplazar; un enlace sin canjear de alguien que dejó el equipo vuelve a servir si lo
  reincorporan; la prueba de la carrera no prueba contención real. Las funciones sólo las ejecuta
  `leda_app`: el comando de consola (P1-3) las llama dentro de `espacio()`; `sesion_vigente` mira la
  membresía activa, no el espacio.
- **P1-2** (`bb5c868c`, escritor delegado): migración `0058`. `tareas_que_ve(persona, vista, ahora)`
  (sólo tareas abiertas; "tus" con `papel` mía / me esperan / espero, leyendo las esperas como el motor;
  "sector" para el referente; "equipo" para la autoridad final) y `vistas_de(persona)`, sin ejecución
  para `leda_app`; la web llama `tareas_de_la_sesion(hash, vista, ahora)` y `vistas_de_la_sesion(hash)`:
  la persona sale de la sesión, nunca del pedido. `vencida` y `bloqueo_abierto` vienen vacíos para quien
  no es el responsable, su referente ni la autoridad. `puede_ver_tarea` no cambió. RED: 15 fallas;
  GREEN: 15 passed. `pytest tests/garantias`: 558 passed. RDD `review-58736fd6bdbafbc8`, aprobada.
  Advertencia sin arreglar: una espera por el bloqueo de quien destraba sigue contando aunque ese bloqueo
  ya se haya resuelto (mientras la tarea siga abierta); sugerencias: probar los negativos de la cadena y
  el borde de `vencida`. Para la P1-3: la cadena de esperas de una tarea trabada necesita su función, y
  `vencida` no mira una nueva previsión de la persona (el motor sí).
- **P1-3** (`b7fd66fb`: migración `0059`, la cadena de esperas de una tarea trabada, hasta 10 niveles y
  sin repetir; `19e922ec`: la API en `src/leda/web_app.py`, enchufada en `entrada.py`): `/app/entrar/{token}`
  (cookie `leda_sesion` `HttpOnly`, `Secure`, `SameSite=Strict`, `Path=/app`, `Max-Age` de 400 días que se
  renueva), `/app/api/yo`, `/app/api/tareas?vista=` (panel, semana, tareas con barra, días que quedan y
  esperas; los vacíos de la base no se completan), `POST /app/salir`; comandos `leda enlace-web` y
  `leda cortar-sesiones-web`. Sus pruebas: 33 passed; `pytest tests/garantias`: 585 passed (el escritor
  escribió el código antes que las pruebas y mostró el RED quitándolo). RDD `review-62fbe1aba719db0b`,
  aprobada. Advertencias: los días que quedan cuando vence el mismo día; `/app/` todavía no se servía (lo
  resuelve la P1-4); sugerencias: el candado global serializa la web, el chequeo de `Origin` detrás de un
  proxy. **Hallazgo del escritor, decidido por el coordinador (técnico):** Telegram abre el enlace para
  armar la vista previa y gastaría el enlace de un solo uso; desde la P1-4, abrir el enlace muestra un
  botón "Entrar" y el canje es al tocarlo.
- **P1-4** (escritor delegado). `5e3d74b3`: abrir el enlace (GET) muestra la misma página con el botón
  "Entrar" para cualquier token y no lo gasta; tocarlo (POST, mismo origen) lo canjea una vez (RED 27
  fallas, GREEN 31 passed); la página del botón manda `Referrer-Policy: same-origin` porque con
  `no-referrer` el navegador manda `Origin: null` y el chequeo lo rechazaría. `3dd40792`: la web en
  `web/` (React 19.1.0, Vite 6.3.5, TypeScript 5.8.3, Tailwind 4.1.11, lucide-react 0.525.0, JetBrains
  Mono local; versiones exactas y `package-lock.json`; `web/dist` y `node_modules` fuera de Git), con
  los tokens de la "9 · Terminal" y las piezas (cabezal, panel, semana, tarjeta, barra de días, árbol de
  esperas, botón inerte, selector de vista, salir); el servidor la sirve en `/app/` con su CSP, sin tapar
  la API. La API suma `dias_de_atraso` para "[VENCIDA +Nd]", sólo cuando la base ya muestra el atraso.
  `b83aae48` y `2731f214`: un comentario que la garantía de capacidades leía como el campo de prioridad,
  y las pruebas de consola que entran con el botón. 390 px: la web servida con datos de mentira en el
  puerto 5179 dentro de un marco de 390 px, sin desbordes (servidor cortado). Comprobado por el
  coordinador: `npm run typecheck` sin errores, `npx vitest run` 27 passed, `npm run build` bien;
  `pytest tests/test_cli_plataforma.py tests/garantias/test_api_de_la_plataforma.py
  tests/garantias/test_web_servida.py`: 56 passed; `pytest tests/garantias` (por el escritor, con
  `test_frontera`, que corre todas en otro proceso, después del arreglo): en verde; nada escuchando en
  8000, 8001, 5173 ni 5179; `_archivo_de_la_web` devuelve `None` ante `../`, `..\`, rutas absolutas y
  `%2e%2e`. RDD por tramos (el `package-lock.json` es generado y no entra en el presupuesto de una
  revisión entera): `review-67a124eeb603558a` (parte A) y `review-c660bc80e653c6df` (la web), aprobadas.
  Advertencias: una doble pulsación rápida en "Entrar" puede caer en "ya no sirve"; una compilación nueva
  mientras alguien navega puede servir un índice que apunta a archivos que ya no están; sugerencias de
  pruebas (401 en tareas, vistas vacías, la semana).
- **P1-5** (`ab3fae1d`): `docs/capacidades.md`, `docs/product/plataforma-pendientes.md` y
  `PRUEBA-LOCAL.md` ("La plataforma web (porción 1)", en el puerto 8001). `PENDIENTE`: la tarjeta no abre
  la página de la tarea (la de hoy entra con un enlace propio, no con la sesión); no hay base para probarla
  de punta a punta todavía: `leda_motor` está en la `0056` y reservada para la prueba por Telegram; al
  juntar las ramas, se pone al día hasta la `0059` (con respaldo) y se prueba ahí.

- **P1-6** (escritor delegado; dos commits de código). `a5e23f73` (P1-6a): migración `0060` con
  su rollback y plegada en `db/esquema.sql`. `tareas_que_ve` da `bloqueo_abierto` para toda tarea
  de la lista (decisión 7; con eso la cadena de la `0059` también cuelga de las ajenas, decisión 6,
  que ya bajaba hasta 10 niveles) y, para quien no ve los atrasos de la tarea, `vencida` recién con
  el atraso hablado, como `informe_al_grupo._sin_entregar`, sólo para una tarea que sigue y ya
  pasada su fecha: (a) su previsión vigente (la última que ninguna otra reemplaza, como
  `ancla.prevision_vigente`) posterior al vencimiento, o (b) el escalamiento de ese vencimiento ya
  salido (`_quedo_asentado_el_atraso`); columna nueva `prevision` (la vigente, si es posterior al
  vencimiento). Lo propio, el sector y el equipo, como antes. `terminadas_que_ve` y
  `terminadas_de_la_sesion`: las terminadas de 30 días por el evento que las terminó, cada vista en
  su alcance; las canceladas, no. `workspace_setting.bot_usuario` con una restricción de formato;
  el pack declara `telegram.bot_usuario` (opcional; `importador.py` lo guarda, avisa si está mal
  escrito y lo borra si se saca) y `/app/api/yo` da `chat_con_leda`. La API devuelve `marcas`
  (trabada y vencida juntas; el panel cuenta las dos), `prevision` y `terminadas`. Archivos del
  pack: `src/leda/importador.py` y `espacios/corework.yaml` (sólo un comentario: el usuario del bot
  de CoreWork queda `PENDIENTE` del usuario; el agente no lo conoce ni lee `.env`). RED: 27 fallas
  (`UndefinedFunction`, columnas que no estaban, nulos); GREEN: `pytest tests/garantias/test_quien_ve_que.py
  tests/garantias/test_api_de_la_plataforma.py`: 65 passed; `pytest tests/garantias/test_migraciones.py
  tests/garantias/test_aislamiento.py tests/test_esqueleto.py`: 36 passed (rollback y paridad);
  `pytest` de la verificación (las dos anteriores, `test_web_servida`, `test_enlace_y_sesion`,
  `test_capacidades`, `test_frontera`, `tests/test_cli_plataforma.py`): 122 passed (9 min 31 s).
  `0a2a6fa9` (P1-6b): la tarjeta muestra todas las marcas ("[TRABADA] [VENCIDA +3d]") y la previsión
  ("19.10 · prevé 28.10"); "Terminadas en los últimos 30 días" aparte, después de las abiertas, con
  quién las hizo en el sector y el equipo; "> consultar a leda" es un enlace a `https://t.me/<bot>`
  (sólo una dirección de Telegram; sin ella, no se muestra). RED: 9 fallas en 5 archivos; GREEN:
  `npx tsc --noEmit` sin errores, `npx vitest run` 38 passed, `npx vite build` bien.
  `PENDIENTE`: el usuario del bot de CoreWork; la suite entera de garantías (la corre el
  coordinador); la revisión RDD de los dos commits.

## Decidido por el usuario (2026-10-12)

Las ocho preguntas de la noche, contestadas antes de la prueba por Telegram. Criterio común del usuario:
la web informa lo mismo que el informe al grupo; informar antes que el silencio.

1. **Lo que espero, como en el informe al grupo.** Marcos ve la fecha y el estado de la tarea de Ariel que
   espera. La marca **[VENCIDA]**, con la previsión nueva si la hay, aparece recién cuando el atraso ya se
   habló en privado con Ariel, igual que en el informe al grupo (`informe_al_grupo._sin_entregar`,
   constitución §8); antes, la fecha sola.
2. **No:** esperar una tarea no habilita a abrir su página.
3. **Sí, las terminadas de los últimos 30 días**, con quién las hizo (las tareas suelen ser largas; una
   semana se queda corta).
4. **Sí:** lo que espera mi revisión queda en "Tus tareas", aunque sea de otra área.
5. **Las dos marcas:** trabada y vencida a la vez lleva **[TRABADA] [VENCIDA]**; trabada en fecha, sólo
   [TRABADA]. La vencida sigue la regla de la 1.
6. **La cadena entera**, todos los escalones: así se ve si se va destrabando.
7. **Sí:** Marcos ve que la tarea de otro que espera está trabada.
8. **El botón dice "> consultar a leda"** y abre el chat de Telegram con el bot del espacio (la dirección
   sale del pack). Un chat propio dentro de la web va a "Anotado para más adelante" del ROADMAP.
